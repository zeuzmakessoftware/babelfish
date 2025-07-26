import aiohttp
import asyncio
import logging
from typing import AsyncGenerator, Optional, Dict, Any
import io

logger = logging.getLogger(__name__)

class RimeVoiceService:
    """Service for integrating with Rime Voice AI"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.rime.ai/v1"
        self.session: Optional[aiohttp.ClientSession] = None
        
        # Voice style mappings
        self.voice_styles = {
            "professional_female": {
                "voice_id": "aurora",
                "style": "professional",
                "language": "en-US"
            },
            "professional_male": {
                "voice_id": "atlas",
                "style": "professional", 
                "language": "en-US"
            },
            "conversational_female": {
                "voice_id": "bella",
                "style": "conversational",
                "language": "en-US"
            },
            "conversational_male": {
                "voice_id": "caleb",
                "style": "conversational",
                "language": "en-US"
            }
        }
    
    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self.session
    
    async def synthesize_speech(
        self, 
        text: str, 
        voice_style: str = "professional_female",
        speed: float = 1.0,
        output_format: str = "mp3"
    ) -> AsyncGenerator[bytes, None]:
        """
        Synthesize speech using Rime Voice AI
        
        Args:
            text: Text to synthesize
            voice_style: Voice style to use
            speed: Speech speed (0.5 - 2.0)
            output_format: Output format (mp3, wav, ogg)
            
        Yields:
            Audio data chunks
        """
        try:
            session = await self._get_session()
            
            # Get voice configuration
            voice_config = self.voice_styles.get(voice_style, self.voice_styles["professional_female"])
            
            # Prepare request payload
            payload = {
                "text": text,
                "voice": {
                    "voice_id": voice_config["voice_id"],
                    "style": voice_config["style"],
                    "language": voice_config["language"]
                },
                "audio_config": {
                    "format": output_format,
                    "sample_rate": 22050,
                    "speed": speed,
                    "pitch": 0,
                    "volume": 1.0
                },
                "streaming": True
            }
            
            logger.info(f"Synthesizing speech with Rime: {len(text)} characters")
            
            async with session.post(f"{self.base_url}/speech/synthesize", json=payload) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Rime API error: {response.status} - {error_text}")
                    raise Exception(f"Speech synthesis failed: {error_text}")
                
                # Stream audio data
                async for chunk in response.content.iter_chunked(8192):
                    yield chunk
                    
        except Exception as e:
            logger.error(f"Speech synthesis error: {str(e)}")
            # Fallback to empty audio stream
            yield b""
    
    async def get_available_voices(self) -> Dict[str, Any]:
        """Get list of available voices from Rime"""
        try:
            session = await self._get_session()
            
            async with session.get(f"{self.base_url}/voices") as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to fetch voices: {response.status}")
                    return {"voices": []}
                    
        except Exception as e:
            logger.error(f"Error fetching voices: {str(e)}")
            return {"voices": []}
    
    async def analyze_audio_quality(self, audio_data: bytes) -> Dict[str, Any]:
        """Analyze synthesized audio quality"""
        try:
            # This would implement quality analysis
            # For now, return mock metrics
            return {
                "quality_score": 0.95,
                "clarity": 0.92,
                "naturalness": 0.97,
                "prosody": 0.94,
                "duration_ms": len(audio_data) * 0.046  # Rough estimation
            }
        except Exception as e:
            logger.error(f"Audio quality analysis error: {str(e)}")
            return {"quality_score": 0.0}
    
    async def batch_synthesize(
        self, 
        texts: list[str], 
        voice_style: str = "professional_female"
    ) -> Dict[str, AsyncGenerator[bytes, None]]:
        """Synthesize multiple texts in parallel"""
        try:
            tasks = []
            for i, text in enumerate(texts):
                task = asyncio.create_task(
                    self._synthesize_to_bytes(text, voice_style, f"batch_{i}")
                )
                tasks.append(task)
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            batch_results = {}
            for i, result in enumerate(results):
                if isinstance(result, Exception):
                    logger.error(f"Batch synthesis error for text {i}: {result}")
                    batch_results[f"batch_{i}"] = self._empty_audio_generator()
                else:
                    batch_results[f"batch_{i}"] = result
            
            return batch_results
            
        except Exception as e:
            logger.error(f"Batch synthesis error: {str(e)}")
            return {}
    
    async def _synthesize_to_bytes(self, text: str, voice_style: str, batch_id: str) -> AsyncGenerator[bytes, None]:
        """Helper method for batch synthesis"""
        try:
            async for chunk in self.synthesize_speech(text, voice_style):
                yield chunk
        except Exception as e:
            logger.error(f"Error in batch item {batch_id}: {str(e)}")
            yield b""
    
    async def _empty_audio_generator(self) -> AsyncGenerator[bytes, None]:
        """Empty audio generator for error cases"""
        yield b""
    
    async def close(self):
        """Close the aiohttp session"""
        if self.session and not self.session.closed:
            await self.session.close()
            
    def __del__(self):
        """Cleanup on deletion"""
        if hasattr(self, 'session') and self.session and not self.session.closed:
            asyncio.create_task(self.session.close()) 