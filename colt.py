import os.path
import subprocess
import sublime

from xml.etree.ElementTree import Element, SubElement, tostring, parse

class ColtPreferences(object):
        NAME = "Preferences.sublime-settings"

def isColtFile(view):
        if view.file_name() is None :
                return False

        filename = view.file_name().lower()
        return filename.endswith(".js") or filename.endswith(".htm") or filename.endswith(".html")

def getProjectWorkingDir(projectPath): 
        storageFilePath = os.path.expanduser("~") + os.sep + ".colt" + os.sep + "storage.xml"

        if not os.path.exists(storageFilePath) :
                return None

        projectSubDir = None
        storageRootElement = parse(storageFilePath).getroot()
        for storageElement in storageRootElement :
                if storageElement.attrib["path"] == projectPath :
                        projectSubDir = storageElement.attrib["subDir"]
                        break

        if projectSubDir is None :
                return None

        return os.path.expanduser("~") + os.sep + ".colt" + os.sep + "storage" + os.sep + projectSubDir

def addToWorkingSet(newProjectPath):
        workingSetFilePath = os.path.expanduser("~") + os.sep + ".colt" + os.sep + "workingset.xml"
        projectsList = []

        # Populate projects list
        if os.path.exists(workingSetFilePath) :
                workingSetElement = parse(workingSetFilePath).getroot()
                for projectElement in workingSetElement :
                        projectPath = projectElement.attrib["path"]
                        if projectPath :
                                projectsList.append(projectPath)

        # Remove project path from the list
        projectsList = filter(lambda projectPath : projectPath != newProjectPath, projectsList)

        # Push new project
        projectsList.insert(0, newProjectPath)

        # Save the list
        workingSetElement = Element("workingset")
        workingSetElement.set("openRecent", "true")

        for projectPath in projectsList :
                projectElement = SubElement(workingSetElement, "project")
                projectElement.set("path", projectPath)

        workingSetFile = open(workingSetFilePath, "w")
        workingSetFile.write(tostring(workingSetElement))
        workingSetFile.close()

def runCOLT(settings):
        coltPath = settings.get("coltPath")

        platform = sublime.platform()
        if platform == "osx" :
                subprocess.Popen(["open", "-n", "-a", coltPath])
        elif platform == "windows" :
                subprocess.Popen([coltPath + "\\colt.exe"]) 
        else :
                sublime.error_message("Unsupported platform: " + platform)

def exportProject(window):
        mainDocumentPath = window.active_view().file_name()
        mainDocumentName = os.path.splitext(os.path.basename(mainDocumentPath))[0]
        basedir = os.path.dirname(mainDocumentPath) # TODO: ask user for base dir?

        # Root
        rootElement = Element("xml")

        rootElement.set("projectName", mainDocumentName)
        rootElement.set("projectType", "JS")

        # Paths
        pathsElement = SubElement(rootElement, "paths")
        createElement("sources-set", "**/*.js, -lib/*.js", pathsElement)
        createElement("excludes-set", "out/**, .git/**, .*/**, **/*bak___", pathsElement)
        createElement("reloads-set", "**/*.htm*, **/*.css, **/*.png", pathsElement)        

        # Build
        buildElement = SubElement(rootElement, "build")
        createElement("main-document", mainDocumentPath, buildElement)
        createElement("use-custom-output-path", "false", buildElement)
        createElement("out-path", "", buildElement)

        # Live
        liveElement = SubElement(rootElement, "live")
        # Settings
        settingsElement = SubElement(liveElement, "settings")
        createElement("clear-log", "false", settingsElement)
        createElement("disconnect", "true", settingsElement)

        # Launch
        launchElement = SubElement(liveElement, "launch")
        createElement("launcher", "DEFAULT", launchElement)

        # Inner live
        innerLiveElement = SubElement(liveElement, "live")
        createElement("paused", "false", innerLiveElement)
        createElement("max-loop", "10000", innerLiveElement)
        createElement("live-html-edit", "true", innerLiveElement)
        createElement("disable-in-minified", "true", innerLiveElement)

        coltProjectFilePath = basedir + os.sep + "autogenerated.colt"
        coltProjectFile = open(coltProjectFilePath, "w")
        coltProjectFile.write(tostring(rootElement))
        coltProjectFile.close()

        return coltProjectFilePath

def createElement(name, value, parentElement):
        element = SubElement(parentElement, name)
        element.text = value
        return element                       