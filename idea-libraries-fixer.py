import os
import re
import sys

def findAllArtifactDirectories(mavenRepositoryRoot, baseDirectory, paths):
  for path in os.listdir(os.path.join(mavenRepositoryRoot, baseDirectory)):
    if os.path.isdir(os.path.join(mavenRepositoryRoot, baseDirectory, path)):
      findAllArtifactDirectories(mavenRepositoryRoot, os.path.join(baseDirectory, path), paths)
    elif path == '_remote.repositories':
      paths.update([baseDirectory])

def findAllPossibleArtifactDescriptors(mavenRepositoryRoot):
  artifactDirectories = set()
  findAllArtifactDirectories(mavenRepositoryRoot, '', artifactDirectories)

  artifactDescriptors = {}
  for path in artifactDirectories:
    descriptor = re.sub(r'[\/\.\-]', '_', path)
    artifactDescriptors[descriptor] = path

  return artifactDescriptors

def findArtifactRepositorySubPath(artifactorDescriptors, descriptor):
  while descriptor and not descriptor in artifactDescriptors:
    descriptor = descriptor[:-1]

  return artifactDescriptors[descriptor]

def determineArtifactProperties(repositorySubPath):  
  version = os.path.basename(repositorySubPath)
  repositorySubPath = os.path.dirname(repositorySubPath)

  groupId = os.path.dirname(repositorySubPath).replace('/', '.')
  artifactId = os.path.basename(repositorySubPath)

  return (groupId, artifactId, version)

def readMavenLibraryDescriptorFile(path):
  descriptorFile = open(path, 'r')
  contents = descriptorFile.read()
  descriptorFile.close()
  return contents

def generateMavenLibraryDescriptorFileContents(repositorySubPath, groupId, artifactId, version):
  artifactBasePath = os.path.join(repositorySubPath, artifactId + "-" + version)

  return """<component name="libraryTable">
  <library name="Maven: """ + ':'.join([groupId, artifactId, version]) + """">
    <CLASSES>
      <root url="jar://$MAVEN_REPOSITORY$/""" + artifactBasePath + """.jar!/" />
    </CLASSES>
    <JAVADOC>
      <root url="jar://$MAVEN_REPOSITORY$/""" + artifactBasePath + """-javadoc.jar!/" />
    </JAVADOC>
    <SOURCES>
      <root url="jar://$MAVEN_REPOSITORY$/""" + artifactBasePath + """-sources.jar!/" />
    </SOURCES>
  </library>
</component>"""

def writeMavenLibraryDescriptorFile(path, contents):
  descriptorFile = open(path, 'w')
  descriptorFile.write(contents)
  descriptorFile.close()

if len(sys.argv) < 3:
  print 'Usage: python ' + sys.argv[0] + ' <path-to-idea-folder> <path-to-maven-repository-folder>'
  print '  Example: python ' + sys.argv[0] + ' ~/work/my-project/.idea ~/.m2/repository'
  exit(-1)

ideaRoot = sys.argv[1]
mavenRepositoryRoot = sys.argv[2]

ideaMavenLibrariesDirectory = os.path.join(ideaRoot, 'libraries')
mavenLibraryDescriptorFilePattern = re.compile('Maven__(.*)\.xml')

artifactDescriptors = findAllPossibleArtifactDescriptors(mavenRepositoryRoot)

for path in os.listdir(ideaMavenLibrariesDirectory):
  match = mavenLibraryDescriptorFilePattern.match(path)
  if match:
    pathDescriptor = match.group(1)

    repositorySubPath = findArtifactRepositorySubPath(artifactDescriptors, pathDescriptor)
    (groupId, artifactId, version) = determineArtifactProperties(repositorySubPath)

    fullyQualifiedArtifact = ':'.join([groupId, artifactId, version])

    descriptorFile = os.path.join(ideaMavenLibrariesDirectory, path)
    descriptorContents = readMavenLibraryDescriptorFile(descriptorFile)

    if not fullyQualifiedArtifact in descriptorContents:
      print '\n=========================================================================================='
      print 'IDEA Maven library descriptor file ' + path + ' for artifact ' + fullyQualifiedArtifact + ' is corrupt'
      print '\nCorrupt contents:\n' + descriptorContents
      newContents = generateMavenLibraryDescriptorFileContents(repositorySubPath, groupId, artifactId, version)
      print '\nNew contents:\n' + newContents
      print '=========================================================================================='

      writeMavenLibraryDescriptorFile(descriptorFile, newContents)
