import json
import falcon

import sim_racing_tools.automation.sandbox as sandbox


class EngineJsonResource:
    def on_get(self, req, resp):
        doc = sandbox.get_all_engines_data()
        resp.text = json.dumps(doc, ensure_ascii=False)
        resp.content_type = falcon.MEDIA_JSON
        resp.status = falcon.HTTP_200
