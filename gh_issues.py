from xml.etree import ElementTree


class Issue(object):

    __slots__ = ['artifact_id', 'submitted_by', 'assigned_to', 'priority'
                 'status', 'resolution', 'summary', 'open_date',
                 'artifact_type', 'category', 'artifact_group_id', 'details',
                 'artifact_history']


class History(object):

    __slots__ = []


root = ElementTree.parse('sf_export.xml').getroot()

[artifacts, tasks, documents, news]  = root.getchildren()

for artifact in artifacts:
    for field in artifact.getchildren():
        print field.attrib, field.getchildren()
        if field.attrib['name'] == 'artifact_history':
            print field.getchildren()[0].getchildren()
    break

