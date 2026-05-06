from atlassian import Jira

class JiraClient:
    def __init__(self, server, email, token):
        self.server = server
        self.email = email
        self.token = token
        self.jira = None

    def connect(self):
        try:
            print(f"Connecting to Jira: {self.server}")
            self.jira = jira.Jira(server=self.server, basic_auth=(self.email, self.token))
            # Test connection by getting current user
            user = self.jira.myself()
            print(f"Connected as: {user['displayName']}")
            return True
        except Exception as e:
            print(f"Connection failed: {type(e).__name__}: {e}")
            import traceback
            traceback.print_exc()
            return False
