import logging
import json
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ENH_JSON:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "json_text": ("STRING", {"multiline": True}),
            }
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("output1", "output2", "output3", "output4")
    FUNCTION = "extract_prompts"
    CATEGORY = "Custom-Nodes"

    def extract_prompts(self, json_text):
        """
        Extract 4 prompts from JSON input and return them as separate outputs.
        Falls back to "photo of an unimpressed white cat" for any failed extractions.
        
        Expected JSON format:
        {
          "prompt1": "text here",
          "prompt2": "text here", 
          "prompt3": "text here",
          "prompt4": "text here"
        }
        
        Alternative supported format:
        {
          "prompts": ["text1", "text2", "text3", "text4"]
        }
        """
        fallback = "photo of an unimpressed white cat"
        
        try:
            # Enhanced markdown code block detection and removal
            cleaned_json = json_text.strip()
            
            # Detect and remove various markdown code block patterns
            # Pattern 1: ```json ... ```
            if '```json' in cleaned_json:
                cleaned_json = re.sub(r'^.*?```json\s*\n?', '', cleaned_json, flags=re.DOTALL)
                cleaned_json = re.sub(r'\n?\s*```.*?$', '', cleaned_json, flags=re.DOTALL)
            
            # Pattern 2: ``` ... ``` (generic code blocks)
            elif cleaned_json.startswith('```') and cleaned_json.endswith('```'):
                cleaned_json = re.sub(r'^```[a-zA-Z]*\s*\n?', '', cleaned_json)
                cleaned_json = re.sub(r'\n?\s*```$', '', cleaned_json)
            
            # Pattern 3: Single backticks `...`
            elif cleaned_json.startswith('`') and cleaned_json.endswith('`'):
                cleaned_json = cleaned_json.strip('`').strip()
            
            # Remove any remaining markdown artifacts
            cleaned_json = re.sub(r'^```[a-zA-Z]*\s*\n?', '', cleaned_json, flags=re.MULTILINE)
            cleaned_json = re.sub(r'\n?\s*```\s*$', '', cleaned_json, flags=re.MULTILINE)
            
            # Fix common LLM JSON formatting issues
            # Remove trailing commas before closing braces/brackets
            cleaned_json = re.sub(r',(\s*[}\]])', r'\1', cleaned_json)
            
            # MOST IMPORTANT: Fix the exact pattern from user's example
            # Remove quote-only lines before closing braces
            cleaned_json = re.sub(r'"\s*\n\s*"\s*\n\s*}', '"\n}', cleaned_json)
            cleaned_json = re.sub(r'"\s*\n\s*"(?=\s*\n\s*})', '"', cleaned_json) 
            
            # Remove standalone quote lines anywhere
            cleaned_json = re.sub(r'\n\s*"\s*\n(?=\s*})', '\n', cleaned_json)
            
            # Very direct: if there's \" \n } pattern, fix it
            cleaned_json = re.sub(r'"\s*\n\s*}', '"\n}', cleaned_json)
            
            # Remove extra quotes after closing braces  
            cleaned_json = re.sub(r'}"\s*$', '}', cleaned_json.strip())
            
            # Remove any trailing quotes or characters after the final }
            cleaned_json = re.sub(r'}\s*[^}]*$', '}', cleaned_json.strip())
            
            # Final cleanup - ensure we have clean JSON bounds
            cleaned_json = cleaned_json.strip()
            
            logger.info(f"Original JSON length: {len(json_text)}")
            logger.info(f"Cleaned JSON length: {len(cleaned_json)}")
            logger.info(f"Cleaned JSON preview: {cleaned_json[:200]}...")
            logger.info(f"Cleaned JSON ending: ...{cleaned_json[-50:]}")
            
            # Parse the JSON
            data = json.loads(cleaned_json)
            
            # Method 1: Direct prompt1-prompt4 keys
            if all(f"prompt{i}" in data for i in range(1, 5)):
                output1 = str(data.get("prompt1", fallback)).strip()
                output2 = str(data.get("prompt2", fallback)).strip()
                output3 = str(data.get("prompt3", fallback)).strip()
                output4 = str(data.get("prompt4", fallback)).strip()
                
            # Method 2: Array format in "prompts" key
            elif "prompts" in data and isinstance(data["prompts"], list):
                prompts = data["prompts"]
                output1 = str(prompts[0]).strip() if len(prompts) > 0 else fallback
                output2 = str(prompts[1]).strip() if len(prompts) > 1 else fallback
                output3 = str(prompts[2]).strip() if len(prompts) > 2 else fallback
                output4 = str(prompts[3]).strip() if len(prompts) > 3 else fallback
                
            # Method 3: Complex format with prompt objects (extracts "prompt" field)
            elif "prompts" in data and isinstance(data["prompts"], list) and len(data["prompts"]) > 0:
                if isinstance(data["prompts"][0], dict):
                    prompts = data["prompts"]
                    output1 = str(prompts[0].get("prompt", fallback)).strip() if len(prompts) > 0 else fallback
                    output2 = str(prompts[1].get("prompt", fallback)).strip() if len(prompts) > 1 else fallback
                    output3 = str(prompts[2].get("prompt", fallback)).strip() if len(prompts) > 2 else fallback
                    output4 = str(prompts[3].get("prompt", fallback)).strip() if len(prompts) > 3 else fallback
                else:
                    # Fallback to all defaults
                    output1 = output2 = output3 = output4 = fallback
            else:
                # No recognized format
                output1 = output2 = output3 = output4 = fallback
                
        except (json.JSONDecodeError, KeyError, IndexError, TypeError) as e:
            logger.error(f"JSON parsing failed: {e}")
            logger.error(f"Cleaned JSON content: {repr(cleaned_json)}")
            
            # Try to identify the specific issue
            if '"' in cleaned_json[-20:]:
                logger.error("Possible stray quote at end of JSON")
            if ',' in cleaned_json[-20:]:
                logger.error("Possible trailing comma issue")
                
            # Return fallback for all outputs
            output1 = output2 = output3 = output4 = fallback
        
        # Ensure none are empty
        output1 = output1 if output1 else fallback
        output2 = output2 if output2 else fallback
        output3 = output3 if output3 else fallback
        output4 = output4 if output4 else fallback
        
        logger.info(f"Extracted prompts:")
        logger.info(f"Output1: {output1}")
        logger.info(f"Output2: {output2}")
        logger.info(f"Output3: {output3}")
        logger.info(f"Output4: {output4}")
        
        return (output1, output2, output3, output4)

NODE_CLASS_MAPPINGS = {
    "ENH_JSON": ENH_JSON
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ENH_JSON": "ENH JSON Prompt Extractor"
}