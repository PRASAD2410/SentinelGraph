"""Gemini adapter. Keys stay in .env and never reach the browser."""
import json, os, re, logging, requests
logger=logging.getLogger(__name__)

class GeminiProvider:
    def __init__(self): self.key=os.getenv('GEMINI_API_KEY','').strip(); self.model=os.getenv('GEMINI_MODEL','gemini-3.5-flash-lite')
    @property
    def available(self): return bool(self.key)
    def generate(self,prompt,json_mode=False):
        if not self.available: return None
        url=f'https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.key}'
        config={'temperature':.15,'maxOutputTokens':1800}
        if json_mode: config['responseMimeType']='application/json'
        try:
            r=requests.post(url,json={'contents':[{'parts':[{'text':prompt}]}],'generationConfig':config},timeout=45); r.raise_for_status()
            text=r.json()['candidates'][0]['content']['parts'][0]['text']
            return json.loads(re.sub(r'^```json\s*|\s*```$','',text.strip())) if json_mode else text
        except requests.HTTPError as exc:
            # Log provider feedback for local troubleshooting; never log the key.
            logger.warning('Gemini request failed: HTTP %s — %s', exc.response.status_code, exc.response.text[:500])
            return None
        except requests.RequestException as exc:
            logger.warning('Gemini network request failed: %s', exc)
            return None
        except (KeyError, ValueError, TypeError) as exc:
            logger.warning('Gemini response could not be read: %s', exc)
            return None
    def extract(self,text):
        return self.generate('''Extract only explicit facts from this submitted document. Return JSON only with `entities` and `relationships`. Entity type must be Person, Phone, Vehicle, Location, Account, Organization, or Event. Entity fields: label,type,confidence. Relationship fields: source_label,target_label,type,confidence. Do not infer criminality.\nDOCUMENT:\n'''+text[:30000],True)
def get_llm_provider(): return GeminiProvider()
