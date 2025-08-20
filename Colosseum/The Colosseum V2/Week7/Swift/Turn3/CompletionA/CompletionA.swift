import Cocoa

class ViewController: NSViewController {

    @IBOutlet weak var exportWrongBulletImageButton: NSButton!
    @IBOutlet weak var exportAccurateBulletImageButton: NSButton!
    @IBOutlet var questionArrayController: NSArrayController!

    @IBAction func selectLocationToSaveImage(_ sender: Any) {
        guard 
            let chosenQuestionItem = questionArrayController.selectedObjects as? [Question],
            let clickedButton = sender as? NSButton, 
            let currentQuestion = chosenQuestionItem.first 
        else { 
            return 
        }

        let savePanel = NSSavePanel()
        savePanel.title = "Choose a location to save the bullet PDF."

        if clickedButton.identifier == exportWrongBulletImageButton.identifier {
            savePanel.nameFieldStringValue = currentQuestion.wrongBulletImageFileName ?? "WrongBullet.pdf"
        } else if clickedButton.identifier == exportAccurateBulletImageButton.identifier {
            savePanel.nameFieldStringValue = currentQuestion.accurateBulletImageFileName ?? "AccurateBullet.pdf"
        }

        savePanel.beginSheetModal(for: view.window!) { result in
            if result == .OK, let fileURL = savePanel.url {
                self.handleSelectedFile(at: fileURL, for: currentQuestion, sender: clickedButton)
            }
        }
    }

    private func handleSelectedFile(at url: URL, for question: Question, sender: NSButton) {
        do {
            let data = try Data(contentsOf: url)
            let fileName = url.lastPathComponent

            if sender.identifier == exportWrongBulletImageButton.identifier {
                question.wrongBulletImage = data
                question.wrongBulletImageFileName = fileName
                exportWrongBulletPDF(data: data)
            } else if sender.identifier == exportAccurateBulletImageButton.identifier {
                question.accurateBulletImage = data
                question.accurateBulletImageFileName = fileName
                exportAccurateBulletPDF(data: data)
            }

        } catch {
            print("Error occurred while attempting to read/save image data: \(error)")
        }
    }

    private func exportWrongBulletPDF(data: Data) {
        // Your implementation for exporting Wrong Bullet PDF
    }

    private func exportAccurateBulletPDF(data: Data) {
        // Your implementation for exporting Accurate Bullet PDF
    }
}
