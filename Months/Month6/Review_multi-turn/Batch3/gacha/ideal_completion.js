// ideal_completion.js
function drawGacha(pityCounter, gachaItems) {
    const rand = Math.random();
    let cumulativeProbability = 0;
    let selectedItem = null;

    // Ensure the sum of probabilities are 1
    const totalProbability = gachaItems.reduce((acc, item) => acc + item.probability, 0);
    if (totalProbability!== 1) {
        throw new Error('The sum of all probabilities must be 1');
    }
    

    for (let i = 0; i < gachaItems.length; i++) {
        cumulativeProbability += gachaItems[i].probability;
        if (rand < cumulativeProbability) {
            selectedItem = gachaItems[i].name;
            break;
        }
    }

    // Increment the pity counter with every draw
    pityCounter++;

    const maxPity = 90; // Set your maximum pity threshold
    if (pityCounter >= maxPity) {
        // Reset the pity counter
        pityCounter = 0;

        // Force a 4-star item if the pity counter reaches the threshold
        const fourStarItems = gachaItems.filter(item => item.star === 4);
        if (fourStarItems.length > 0) {
            selectedItem = fourStarItems[Math.floor(Math.random() * fourStarItems.length)].name;
        }
    }

    return {
        SelectedItem: selectedItem,
        pityCounter: pityCounter
      };
}
