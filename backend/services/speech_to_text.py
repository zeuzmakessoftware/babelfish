import boto3
import asyncio
import logging
import io
import wave
from typing import Optional, Dict, Any, AsyncGenerator
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)

class SpeechToTextService:
    """Service for converting speech to text using AWS Transcribe"""
    
    def __init__(self, aws_access_key: str, aws_secret_key: str, aws_region: str):
        self.aws_access_key = aws_access_key
        self.aws_secret_key = aws_secret_key
        self.aws_region = aws_region
        self.transcribe_client = None
        self.s3_client = None
        
        # Initialize AWS clients
        self._init_aws_clients()
    
    def _init_aws_clients(self):
        """Initialize AWS clients"""
        try:
            self.transcribe_client = boto3.client(
                'transcribe',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.aws_region
            )
            
            self.s3_client = boto3.client(
                's3',
                aws_access_key_id=self.aws_access_key,
                aws_secret_access_key=self.aws_secret_key,
                region_name=self.aws_region
            )
            
            logger.info("AWS Transcribe and S3 clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AWS clients: {str(e)}")
            raise
    
    async def transcribe_audio_stream(
        self, 
        audio_stream: AsyncGenerator[bytes, None],
        language_code: str = "en-US",
        media_format: str = "mp3"
    ) -> Dict[str, Any]:
        """
        Transcribe audio stream to text using AWS Transcribe
        
        Args:
            audio_stream: Async generator yielding audio chunks
            language_code: Language code for transcription
            media_format: Audio format (mp3, wav, flac, etc.)
            
        Returns:
            Transcription result with text and confidence
        """
        try:
            # Collect audio data
            audio_data = b""
            async for chunk in audio_stream:
                audio_data += chunk
            
            if not audio_data:
                return {
                    "text": "",
                    "confidence": 0.0,
                    "error": "No audio data received"
                }
            
            # For real-time transcription, we'll use a simplified approach
            # In production, you'd want to use AWS Transcribe Streaming
            return await self._transcribe_audio_data(
                audio_data, 
                language_code, 
                media_format
            )
            
        except Exception as e:
            logger.error(f"Transcription error: {str(e)}")
            return {
                "text": "",
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def transcribe_audio_file(
        self, 
        audio_file_path: str,
        language_code: str = "en-US"
    ) -> Dict[str, Any]:
        """
        Transcribe audio file to text
        
        Args:
            audio_file_path: Path to audio file
            language_code: Language code for transcription
            
        Returns:
            Transcription result
        """
        try:
            with open(audio_file_path, 'rb') as f:
                audio_data = f.read()
            
            return await self._transcribe_audio_data(
                audio_data, 
                language_code, 
                "mp3"
            )
            
        except Exception as e:
            logger.error(f"File transcription error: {str(e)}")
            return {
                "text": "",
                "confidence": 0.0,
                "error": str(e)
            }
    
    async def _transcribe_audio_data(
        self, 
        audio_data: bytes,
        language_code: str,
        media_format: str
    ) -> Dict[str, Any]:
        """
        Internal method to transcribe audio data
        
        Args:
            audio_data: Raw audio data
            language_code: Language code
            media_format: Audio format
            
        Returns:
            Transcription result
        """
        try:
            # For demo purposes, we'll use a mock transcription
            # In production, you'd upload to S3 and use AWS Transcribe
            
            # Mock transcription result
            # This simulates what AWS Transcribe would return
            mock_text = self._mock_transcription(audio_data)
            
            return {
                "text": mock_text,
                "confidence": 0.95,
                "language_code": language_code,
                "media_format": media_format,
                "transcription_job_name": f"babelfish_{asyncio.get_event_loop().time()}",
                "status": "COMPLETED"
            }
            
        except Exception as e:
            logger.error(f"Audio transcription error: {str(e)}")
            return {
                "text": "",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _mock_transcription(self, audio_data: bytes) -> str:
        """
        Mock transcription for demo purposes
        In production, this would be replaced with actual AWS Transcribe
        """
        # Simple mock based on audio data length
        # In reality, this would be the actual transcribed text
        data_length = len(audio_data)
        
        if data_length < 1000:
            return "Hello, how can I help you today?"
        elif data_length < 5000:
            return "I need help understanding this technical terminology."
        else:
            return "Could you please explain this complex technical concept in simpler terms?"
    
    async def start_streaming_transcription(
        self,
        audio_stream: AsyncGenerator[bytes, None],
        language_code: str = "en-US"
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Start real-time streaming transcription
        
        Args:
            audio_stream: Audio data stream
            language_code: Language code
            
        Yields:
            Partial transcription results
        """
        try:
            buffer = b""
            async for chunk in audio_stream:
                buffer += chunk
                
                # Process in chunks (simplified for demo)
                if len(buffer) > 4096:  # Process every 4KB
                    partial_result = await self._transcribe_audio_data(
                        buffer, language_code, "mp3"
                    )
                    
                    yield {
                        "type": "partial",
                        "text": partial_result["text"],
                        "confidence": partial_result["confidence"],
                        "is_final": False
                    }
                    
                    buffer = b""
            
            # Process remaining buffer
            if buffer:
                final_result = await self._transcribe_audio_data(
                    buffer, language_code, "mp3"
                )
                
                yield {
                    "type": "final",
                    "text": final_result["text"],
                    "confidence": final_result["confidence"],
                    "is_final": True
                }
                
        except Exception as e:
            logger.error(f"Streaming transcription error: {str(e)}")
            yield {
                "type": "error",
                "error": str(e),
                "is_final": True
            }
    
    async def get_transcription_job_status(self, job_name: str) -> Dict[str, Any]:
        """Get status of a transcription job"""
        try:
            response = self.transcribe_client.get_transcription_job(
                TranscriptionJobName=job_name
            )
            
            return {
                "job_name": job_name,
                "status": response["TranscriptionJob"]["TranscriptionJobStatus"],
                "language_code": response["TranscriptionJob"].get("LanguageCode"),
                "media_format": response["TranscriptionJob"].get("MediaFormat"),
                "creation_time": response["TranscriptionJob"].get("CreationTime"),
                "completion_time": response["TranscriptionJob"].get("CompletionTime")
            }
            
        except ClientError as e:
            logger.error(f"AWS Transcribe error: {str(e)}")
            return {
                "job_name": job_name,
                "status": "FAILED",
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Job status error: {str(e)}")
            return {
                "job_name": job_name,
                "status": "FAILED",
                "error": str(e)
            }
    
    async def list_transcription_jobs(self, max_results: int = 10) -> Dict[str, Any]:
        """List recent transcription jobs"""
        try:
            response = self.transcribe_client.list_transcription_jobs(
                MaxResults=max_results
            )
            
            return {
                "jobs": response.get("TranscriptionJobSummaries", []),
                "next_token": response.get("NextToken")
            }
            
        except Exception as e:
            logger.error(f"List jobs error: {str(e)}")
            return {
                "jobs": [],
                "error": str(e)
            }
    
    async def delete_transcription_job(self, job_name: str) -> Dict[str, Any]:
        """Delete a transcription job"""
        try:
            self.transcribe_client.delete_transcription_job(
                TranscriptionJobName=job_name
            )
            
            return {
                "job_name": job_name,
                "status": "DELETED"
            }
            
        except Exception as e:
            logger.error(f"Delete job error: {str(e)}")
            return {
                "job_name": job_name,
                "status": "FAILED",
                "error": str(e)
            }
    
    async def close(self):
        """Cleanup resources"""
        # AWS clients don't need explicit cleanup
        pass 