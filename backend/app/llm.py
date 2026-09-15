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
        # A zero temperature makes repeated extraction of the same document much
        # more repeatable. It does not replace analyst review.
        config={'temperature':0,'maxOutputTokens':3000}
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
        # Gemini accepts far more context than a typical FIR. The cap prevents a
        # malformed upload from consuming an unbounded amount of the free quota.
        document=text[:250000]
        return self.generate('''Read the complete supplied document carefully before answering. Extract every DISTINCT, EXPLICITLY NAMED entity. Pay particular attention to all mobile/telephone numbers, vehicle registrations, account numbers, people, organizations, locations, dates, FIR/case numbers, and events. Preserve digits and identifiers exactly as written.

Return JSON only with keys `entities` and `relationships`. Entity type must be exactly Person, Phone, Vehicle, Location, Account, Organization, or Event. Each entity needs `label`, `type`, and `confidence` (0-1). Each relationship needs `source_label`, `target_label`, `type`, and `confidence` (0-1). Only create a relationship when the document explicitly states or directly describes it. Never infer guilt, criminal status, or missing facts.\nDOCUMENT:\n'''+document,True)
def get_llm_provider(): return GeminiProvider()
