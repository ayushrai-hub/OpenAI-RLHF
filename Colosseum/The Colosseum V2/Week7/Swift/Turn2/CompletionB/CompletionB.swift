@IBAction func selectLocationToSaveImage(_ sender: Any) {
    guard let chosenQuestionItem = questionArrayController.selectedObjects.first as? Question,
          let clickedButton = sender as? NSButton else { return }
    
    let userSelection = NSSavePanel()
    
    // Configure initial filename based on button clicked
    let (imageFileName, isWrongBullet) = clickedButton.identifier == exportWrongBulletImageButton.identifier
        ? (chosenQuestionItem.wrongBulletImageFileName, true)
        : (chosenQuestionItem.accurateBulletImageFileName, false)
    
    userSelection.nameFieldStringValue = imageFileName ?? ""
    userSelection.title = "Choose a location to save the bullet PDF."
    
    userSelection.beginSheetModal(for: view.window!) { result in
        guard result == .OK,
              let url = userSelection.url else { return }
        
        do {
            let data = try Data(contentsOf: url)
            let fileName = url.lastPathComponent
            
            // Update appropriate properties based on button type
            if isWrongBullet {
                chosenQuestionItem.wrongBulletImage = data
                chosenQuestionItem.wrongBulletImageFileName = fileName
            } else {
                chosenQuestionItem.accurateBulletImage = data
                chosenQuestionItem.accurateBulletImageFileName = fileName
            }
            
            // Export PDF (assuming same method can be used for both cases)
            self.exportWrongBulletPDF(data: data)
            
        } catch {
            print("Error while attempting to save the background image to the filesystem.")
        }
    }
}
