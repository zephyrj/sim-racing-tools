import falcon

import sim_racing_tools.automation.resources as automation_resources

app = application = falcon.App()
engines = automation_resources.EngineJsonResource()
app.add_route('/json/automation/engines', engines)
