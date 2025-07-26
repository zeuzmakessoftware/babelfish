import boto3
import json
import logging
import time
from typing import Dict, List, Optional, Any
from botocore.exceptions import ClientError, BotoCoreError

logger = logging.getLogger(__name__)

class AWSBedrockService:
    """Service for integrating with AWS Bedrock for AI analysis"""
    
    def __init__(self, access_key: str, secret_key: str, region: str = "us-east-1"):
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region
        
        # Initialize AWS clients
        self.bedrock_client = None
        self.bedrock_runtime_client = None
        
        # Model configurations
        self.text_model_id = "anthropic.claude-3-haiku-20240307-v1:0"
        self.embedding_model_id = "amazon.titan-embed-text-v2:0"
        
        self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize AWS Bedrock clients"""
        try:
            session = boto3.Session(
                aws_access_key_id=self.access_key,
                aws_secret_access_key=self.secret_key,
                region_name=self.region
            )
            
            self.bedrock_client = session.client('bedrock')
            self.bedrock_runtime_client = session.client('bedrock-runtime')
            
            logger.info("AWS Bedrock clients initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize AWS Bedrock clients: {str(e)}")
            raise
    
    async def analyze_technical_term(
        self,
        term: str,
        existing_definitions: Optional[List[Dict]] = None,
        web_context: Optional[List[Dict]] = None,
        business_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze a technical term using AWS Bedrock
        
        Args:
            term: Technical term to analyze
            existing_definitions: Existing definitions from vector search
            web_context: Web search results for additional context
            business_context: Additional business context
            
        Returns:
            Comprehensive analysis including explanation, category, confidence, etc.
        """
        start_time = time.time()
        
        try:
            # Build comprehensive prompt
            prompt = self._build_analysis_prompt(
                term, existing_definitions, web_context, business_context
            )
            
            # Generate analysis using Claude
            analysis_response = await self._invoke_claude(prompt)
            
            # Generate embedding for the term
            embedding = await self._generate_embedding(term)
            
            # Parse and structure the response
            structured_analysis = self._parse_analysis_response(analysis_response)
            
            processing_time = (time.time() - start_time) * 1000
            
            return {
                **structured_analysis,
                "embedding": embedding,
                "processing_time": processing_time,
                "sources": self._determine_sources(existing_definitions, web_context)
            }
            
        except Exception as e:
            logger.error(f"Technical term analysis failed: {str(e)}")
            return self._fallback_analysis(term, (time.time() - start_time) * 1000)
    
    def _build_analysis_prompt(
        self,
        term: str,
        existing_definitions: Optional[List[Dict]],
        web_context: Optional[List[Dict]],
        business_context: Optional[str]
    ) -> str:
        """Build comprehensive analysis prompt for Claude"""
        
        prompt = f"""You are a technical expert specializing in enterprise technology translation. Your task is to analyze the technical term "{term}" and provide a comprehensive explanation suitable for business stakeholders.

TERM TO ANALYZE: {term}

"""
        
        # Add existing definitions context
        if existing_definitions:
            prompt += "EXISTING KNOWLEDGE BASE:\n"
            for i, definition in enumerate(existing_definitions[:3]):
                prompt += f"{i+1}. {definition.get('term', 'Unknown')}: {definition.get('explanation', 'No explanation')}\n"
            prompt += "\n"
        
        # Add web context
        if web_context:
            prompt += "CURRENT WEB CONTEXT:\n"
            for i, result in enumerate(web_context[:3]):
                prompt += f"{i+1}. {result.get('title', 'Unknown')}: {result.get('snippet', 'No snippet')}\n"
            prompt += "\n"
        
        # Add business context
        if business_context:
            prompt += f"BUSINESS CONTEXT: {business_context}\n\n"
        
        prompt += """INSTRUCTIONS:
Provide a comprehensive analysis in JSON format with the following structure:

{
    "explanation": "A clear, professional explanation (100-200 words) that translates technical jargon into business-friendly language. Focus on practical implications and benefits.",
    "category": "Primary technical category (e.g., 'Architecture', 'DevOps', 'Security', 'Data Science', 'Cloud Computing')",
    "confidence": 0.95,
    "business_impact": "Specific business impact statement (50-75 words) explaining how this technology affects operations, costs, or competitive advantage",
    "related_terms": ["term1", "term2", "term3"],
    "technical_complexity": "low|medium|high",
    "implementation_effort": "minimal|moderate|significant",
    "strategic_value": "operational|tactical|strategic"
}

GUIDELINES:
- Use enterprise-appropriate language
- Focus on business value and practical implications
- Avoid overly technical jargon in explanations
- Provide realistic confidence scores (0.7-0.98)
- Include 3-5 related terms that business users might encounter
- Ensure explanations are actionable for decision-makers

Return ONLY the JSON object, no additional text."""
        
        return prompt
    
    async def _invoke_claude(self, prompt: str) -> str:
        """Invoke Claude model via Bedrock"""
        try:
            request_body = {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4000,
                "temperature": 0.7,
                "top_p": 0.9,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            }
            
            response = self.bedrock_runtime_client.invoke_model(
                modelId=self.text_model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            
            if 'content' in response_body and len(response_body['content']) > 0:
                return response_body['content'][0]['text']
            else:
                raise Exception("Invalid response format from Claude")
                
        except (ClientError, BotoCoreError) as e:
            logger.error(f"AWS Bedrock API error: {str(e)}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Claude invocation error: {str(e)}")
            raise
    
    async def _generate_embedding(self, text: str) -> List[float]:
        """Generate embedding using Amazon Titan"""
        try:
            request_body = {
                "inputText": text,
                "dimensions": 1024,
                "normalize": True
            }
            
            response = self.bedrock_runtime_client.invoke_model(
                modelId=self.embedding_model_id,
                contentType="application/json",
                accept="application/json",
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            return response_body.get('embedding', [])
            
        except Exception as e:
            logger.error(f"Embedding generation error: {str(e)}")
            # Return a zero vector as fallback
            return [0.0] * 1024
    
    def _parse_analysis_response(self, response: str) -> Dict[str, Any]:
        """Parse Claude's JSON response"""
        try:
            # Extract JSON from response (Claude sometimes adds extra text)
            json_start = response.find('{')
            json_end = response.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            json_str = response[json_start:json_end]
            analysis = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['explanation', 'category', 'confidence', 'business_impact']
            for field in required_fields:
                if field not in analysis:
                    raise ValueError(f"Missing required field: {field}")
            
            # Ensure confidence is within valid range
            confidence = float(analysis.get('confidence', 0.5))
            analysis['confidence'] = max(0.0, min(1.0, confidence))
            
            # Ensure related_terms is a list
            if 'related_terms' not in analysis or not isinstance(analysis['related_terms'], list):
                analysis['related_terms'] = []
            
            return analysis
            
        except (json.JSONDecodeError, ValueError) as e:
            logger.error(f"Failed to parse analysis response: {str(e)}")
            logger.error(f"Raw response: {response}")
            raise Exception("Failed to parse AI analysis response")
    
    def _determine_sources(
        self, 
        existing_definitions: Optional[List[Dict]], 
        web_context: Optional[List[Dict]]
    ) -> List[str]:
        """Determine information sources used"""
        sources = []
        
        if existing_definitions:
            sources.append("internal_knowledge_base")
        if web_context:
            sources.append("web_search")
        
        sources.append("ai_analysis")
        return sources
    
    def _fallback_analysis(self, term: str, processing_time: float) -> Dict[str, Any]:
        """Provide fallback analysis when AI fails"""
        return {
            "explanation": f"'{term}' is a technical term that requires further analysis. Our AI systems are continuously learning to provide comprehensive explanations for emerging technologies and methodologies.",
            "category": "Technology",
            "confidence": 0.5,
            "business_impact": "This technology may impact operational efficiency and should be evaluated for strategic implementation potential.",
            "related_terms": [],
            "sources": ["fallback"],
            "processing_time": processing_time,
            "embedding": [0.0] * 1024,
            "technical_complexity": "medium",
            "implementation_effort": "moderate",
            "strategic_value": "tactical"
        }
    
    async def batch_analyze_terms(self, terms: List[str]) -> Dict[str, Dict[str, Any]]:
        """Analyze multiple terms in parallel"""
        try:
            import asyncio
            
            # Create analysis tasks
            tasks = []
            for term in terms:
                task = asyncio.create_task(self.analyze_technical_term(term))
                tasks.append((term, task))
            
            # Execute all tasks
            results = {}
            for term, task in tasks:
                try:
                    analysis = await task
                    results[term] = analysis
                except Exception as e:
                    logger.error(f"Batch analysis failed for term '{term}': {str(e)}")
                    results[term] = self._fallback_analysis(term, 1000.0)
            
            return results
            
        except Exception as e:
            logger.error(f"Batch analysis error: {str(e)}")
            return {}
    
    async def get_model_info(self) -> Dict[str, Any]:
        """Get information about available models"""
        try:
            response = self.bedrock_client.list_foundation_models()
            
            models = []
            for model in response.get('modelSummaries', []):
                models.append({
                    'modelId': model.get('modelId'),
                    'modelName': model.get('modelName'),
                    'providerName': model.get('providerName'),
                    'inputModalities': model.get('inputModalities', []),
                    'outputModalities': model.get('outputModalities', [])
                })
            
            return {
                "available_models": models,
                "current_text_model": self.text_model_id,
                "current_embedding_model": self.embedding_model_id
            }
            
        except Exception as e:
            logger.error(f"Failed to get model info: {str(e)}")
            return {"available_models": [], "error": str(e)} 