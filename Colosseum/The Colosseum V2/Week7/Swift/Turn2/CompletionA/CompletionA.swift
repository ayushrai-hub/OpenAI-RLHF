import Cocoa

class YourViewController: NSViewController {

    @IBOutlet weak var exportWrongBulletImageButton: NSButton!
    @IBOutlet weak var exportAccurateBulletImageButton: NSButton!
    @IBOutlet weak var questionArrayController: NSArrayController!

    @IBAction func selectLocationToSaveImage(_ sender: Any) {
        guard let chosenQuestionItem = questionArrayController.selectedObjects as? [Question],
              let clickedButton = sender as? NSButton else { return }

        let userSelection = NSSavePanel()
        userSelection.title = "Choose a location to save the bullet PDF."

        // Set default file name depending on button clicked
        if clickedButton.identifier == exportWrongBulletImageButton.identifier {
            userSelection.nameFieldStringValue = chosenQuestionItem.first?.wrongBulletImageFileName ?? "WrongBullet.pdf"
        } else if clickedButton.identifier == exportAccurateBulletImageButton.identifier {
            userSelection.nameFieldStringValue = chosenQuestionItem.first?.accurateBulletImageFileName ?? "AccurateBullet.pdf"
        }

        userSelection.beginSheetModal(for: view.window!) { result in
            if result.rawValue == NSApplication.ModalResponse.OK.rawValue {
                self.processSavePanelResponse(userSelection: userSelection, chosenQuestionItem: chosenQuestionItem, sender: clickedButton)
            }
        }
    }

    // MARK: - Private Helper Methods

    private func processSavePanelResponse(userSelection: NSSavePanel, chosenQuestionItem: [Question], sender: NSButton) {
        do {
            guard let url = userSelection.url,
                  let question = chosenQuestionItem.first else { return }

            let data = try Data(contentsOf: url)
            let fileNameAndPath = url.lastPathComponent

            if sender.identifier == exportWrongBulletImageButton.identifier {
                question.wrongBulletImage = data
                question.wrongBulletImageFileName = fileNameAndPath
                exportWrongBulletPDF(data: data)

            } else if sender.identifier == exportAccurateBulletImageButton.identifier {
                question.accurateBulletImage = data
                question.accurateBulletImageFileName = fileNameAndPath
                exportAccurateBulletPDF(data: data)
            }

        } catch {
            print("Error while attempting to save the image to the filesystem: \(error.localizedDescription)")
        }
    }

    private func exportWrongBulletPDF(data: Data) {
        // Your implementation to export wrong bullet PDF
    }

    private func exportAccurateBulletPDF(data: Data) {
        // Your implementation to export accurate bullet PDF
    }
}
