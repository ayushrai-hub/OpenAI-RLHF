import Cocoa

class YourViewController: NSViewController {
    
    // MARK: - IBOutlets
    @IBOutlet weak var exportWrongBulletImageButton: NSButton!
    @IBOutlet weak var exportAccurateBulletImageButton: NSButton!
    
    // Assuming this is your outlet to manage questions
    @IBOutlet weak var questionArrayController: NSArrayController!

    // MARK: - IBAction
    @IBAction func selectLocationToSaveImage(_ sender: Any) {
        // Ensure we have a selected question and button
        guard
            let chosenQuestionItem = questionArrayController.selectedObjects as? [Question],
            let clickedButton = sender as? NSButton,
            let question = chosenQuestionItem.first
        else { return }

        // Configure save panel
        let userSelection = NSSavePanel()
        userSelection.title = "Choose a location to save the bullet PDF."
        userSelection.nameFieldStringValue = initialFileName(for: clickedButton, question: question)
        
        // Present save panel
        userSelection.beginSheetModal(for: view.window!) { result in
            if result == .OK, let url = userSelection.url {
                self.processSavePanelResponse(url: url, clickedButton: clickedButton, question: question)
            }
        }
    }

    // MARK: - Helper Methods
    private func initialFileName(for button: NSButton, question: Question) -> String {
        if button.identifier == exportWrongBulletImageButton.identifier {
            return question.wrongBulletImageFileName ?? "wrong_bullet.pdf"
        } else if button.identifier == exportAccurateBulletImageButton.identifier {
            return question.accurateBulletImageFileName ?? "accurate_bullet.pdf"
        }
        return "bullet.pdf" // Default filename
    }

    private func processSavePanelResponse(url: URL, clickedButton: NSButton, question: Question) {
        do {
            let data = try Data(contentsOf: url)
            let fileNameAndPath = url.lastPathComponent

            if clickedButton.identifier == exportWrongBulletImageButton.identifier {
                question.wrongBulletImage = data
                question.wrongBulletImageFileName = fileNameAndPath
                
                // Export PDF for wrong bullet
                exportBulletPDF(data: data, isAccurate: false)

            } else if clickedButton.identifier == exportAccurateBulletImageButton.identifier {
                question.accurateBulletImage = data
                question.accurateBulletImageFileName = fileNameAndPath
                
                // Export PDF for accurate bullet
                exportBulletPDF(data: data, isAccurate: true)
            }

        } catch {
            print("Error while attempting to save the image to the filesystem: \(error)")
        }
    }

    private func exportBulletPDF(data: Data, isAccurate: Bool) {
        // Replace this with actual export logic
        if isAccurate {
            print("Exporting Accurate Bullet PDF")
        } else {
            print("Exporting Wrong Bullet PDF")
        }
    }
}

// Assuming 'Question' is structured like this:
class Question {
    var accurateBulletImage: Data?
    var wrongBulletImage: Data?
    var accurateBulletImageFileName: String?
    var wrongBulletImageFileName: String?
}
