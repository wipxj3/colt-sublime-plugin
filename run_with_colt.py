import sublime, sublime_plugin
import colt, colt_rpc

from colt import ColtPreferences
from colt_rpc import ColtConnection

class ColtCompletitions(sublime_plugin.EventListener):
        
        def on_query_completions(self, view, prefix, locations):                
                if (ColtConnection.port == -1) :
                        return []

                # TODO: implement
                return [ ("var1\t(COLT suggested)", "var1"), ("var2\t(COLT suggested)", "var2") ]

        def getWordPosition(self, view):
                position = self.getPosition(view)
                return view.word(position).end()

        def getPosition(self, view):
                for sel in view.sel() :
                        return sel

                return None

        def getPositionEnd(self, view):
                position = self.getPosition(view)
                if position is None :
                        return - 1

                return position.end()

        def getContent(self, view):
                return view.substr(sublime.Region(0, view.size()))


class RunWithColtCommand(sublime_plugin.WindowCommand):

        def run(self):
                settings = sublime.load_settings(ColtPreferences.NAME)
                if not settings.has("coltPath") :                        
                        sublime.error_message("COLT path is not specified, please enter the path")
                        self.window.show_input_panel("COLT Path:", "", self.onCOLTPathInput, None, None)
                        return

                settings = sublime.load_settings(ColtPreferences.NAME)
                coltPath = settings.get("coltPath")
                
                if not os.path.exists(coltPath) :
                        sublime.error_message("COLT path specified is invalid, please enter the correct path")
                        self.window.show_input_panel("COLT Path:", "", self.onCOLTPathInput, None, None)
                        return

                settings = sublime.load_settings(ColtPreferences.NAME)
                coltPath = settings.get("coltPath")

                # Export COLT project
                coltProjectFilePath = colt.exportProject(self.window)

                # Add project to workset file
                colt.addToWorkingSet(coltProjectFilePath)

                # Run COLT
                colt_rpc.initAndConnect(settings, coltProjectFilePath)

                # Authorize and start live
                colt_rpc.runAfterAuthorization = colt_rpc.startLive
                colt_rpc.authorize(self.window)                        

        def onCOLTPathInput(self, inputPath):
                if inputPath and os.path.exists(inputPath) :
                        settings = sublime.load_settings(ColtPreferences.NAME)
                        settings.set("coltPath", inputPath)
                        sublime.save_settings(ColtPreferences.NAME)
                        self.run()
                else :
                        sublime.error_message("COLT path specified is invalid")                             
