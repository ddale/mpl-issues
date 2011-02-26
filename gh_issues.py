from xml.etree import ElementTree
import time
from github2.client import Github

# project-specific info
SF_IDS = {
    'Project': 80706,
    'Patches': 560722,
    'Bugs': 560720,
    'Feature Requests': 560723,
    'Support Requests': 560721,
}

issue_priority = {
    'Feature Requests':1, 'Support Requests':2, 'Patches': 3, 'Bugs': 4
    }

SF = 'https://sourceforge.net/tracker/?func=detail&aid=%d&group_id=%d&atid=%d'

USER = 'darrendale'
REPO = 'darrendale/mpl-issues'
TOKEN = open('api_token.txt').readlines()[0][:-1]

class Issue(object):

    __slots__ = ['artifact_id', 'submitted_by', 'assigned_to', 'priority',
                 'status', 'resolution', 'summary', 'open_date',
                 'artifact_type', 'category', 'artifact_group_id', 'details',
                 'history', 'messages', 'sourceforge']

    def __init__(self, artifact):
        self.history = []
        self.messages = []

        for field in artifact.getchildren():
            attrs = field.attrib
            name = attrs['name']
            if name == 'artifact_history':
                for event in field.getchildren():
                    h = History(event)
                    self.history.append(h)
            elif name == 'artifact_messages':
                for message in field.getchildren():
                    m = Message(message)
                    self.messages.append(m)
            else:
                setattr(self, name, field.text)

        self.sourceforge = SF % (
            int(self.artifact_id),
            SF_IDS['Project'],
            SF_IDS[self.artifact_type]
            )

    def __cmp__(self, other):
        s = issue_priority[self.artifact_type]
        o = issue_priority[other.artifact_type]
        if s==0:
            return 0
        return 1 if s > o else -1

    def __str__(self):
        return "%s: %s" % (self.artifact_type, self.summary.encode('utf-8'))


class History(object):

    __slots__ = ['field_name', 'old_value', 'entrydate', 'mod_by']

    def __init__(self, history):
        for field in history.getchildren():
            attrs = field.attrib
            name = attrs['name']
            setattr(self, name, field.text)

    def __str__(self):
        return "* On %s, by %s: %s: %s" % (
            time.ctime(int(self.entrydate)), self.mod_by, self.field_name,
            self.old_value
            )


class Message(object):

    __slots__ = ['adddate', 'user_name', 'body']

    def __init__(self, message):
        for field in message.getchildren():
            attrs = field.attrib
            name = attrs['name']
            setattr(self, name, field.text)

    def __str__(self):
        return "#### On %s, %s wrote:\n%s" % (
            time.ctime(int(self.adddate)), self.user_name, self.body
            )


root = ElementTree.parse('sf_export.xml').getroot()

[artifacts, tasks, documents, news]  = root.getchildren()

issues = []
for artifact in artifacts:
    issue = Issue(artifact)
    if issue.status not in ('Deleted', 'Closed'):
        issues.append(issue)


github = Github(username=USER, api_token=TOKEN, requests_per_second=1)

for issue in sorted(issues):
    if issue.details[:4] in ('2 , ', '3 , ', '4 , '):
        # this is spam
        continue

    body = "[Original report at SourceForge](%s)\n\n%s" % (
        issue.sourceforge, issue.details.encode('utf-8')
        )
    if issue.messages:
        body = "%s\n\n### SourceForge Comments\n" % body
        for message in issue.messages:
            body = "%s\n%s" % (body, message)
    if issue.history:
        body = "%s\n\n### SourceForge History\n" % body
        for event in issue.history:
            body = "%s\n%s" % (body, event)

    gh_issue = github.issues.open(
        REPO,
        title=issue.summary.encode('utf-8'),
        body=body
        )
