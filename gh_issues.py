from xml.etree import ElementTree

# project-specific info
SF_IDS = {
    'Project': 80706,
    'Patches': 560722,
    'Bugs': 560720,
    'Feature Requests': 560723,
    'Support Requests': 560721,
}

s = 'https://sourceforge.net/tracker/?func=detail&aid=%d&group_id=%d&atid=%d'


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

        self.sourceforge = s % (
            int(self.artifact_id),
            SF_IDS['Project'],
            SF_IDS[self.artifact_type]
            )


class History(object):

    __slots__ = ['field_name', 'old_value', 'entrydate', 'mod_by']

    def __init__(self, history):
        for field in history.getchildren():
            attrs = field.attrib
            name = attrs['name']
            setattr(self, name, field.text)


class Message(object):

    __slots__ = ['adddate', 'user_name', 'body']

    def __init__(self, message):
        for field in message.getchildren():
            attrs = field.attrib
            name = attrs['name']
            setattr(self, name, field.text)


root = ElementTree.parse('sf_export.xml').getroot()

[artifacts, tasks, documents, news]  = root.getchildren()

results = []
for artifact in artifacts:
    results.append(Issue(artifact))
