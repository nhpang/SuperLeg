document.addEventListener("DOMContentLoaded", function() {

    balance = 100
    const updatebalance = () => {
        document.getElementById("balance").textContent = "BALANCE: $" + balance
    }
    updatebalance()

    d1 = Math.floor(Math.random() * 13 + 1)
    d2 = Math.floor(Math.random() * 13 + 1)
    d3 = 0
    p1 = Math.floor(Math.random() * 13 + 1)
    p2 = Math.floor(Math.random() * 13 + 1)
    p3 = 0
    
    dealer = [d1,d2]
    player = [p1,p2]

    document.getElementById("hit").disabled = true
    document.getElementById("stand").disabled = true
    document.getElementById("double").disabled = true
    document.getElementById("restart").disabled = false
    document.getElementById("bet").disabled = false

    document.getElementById("title").textContent = "BLACKJACK"
    document.getElementById("title").setAttribute("style", "color:white") 

    player.forEach(() => {
        let card = document.createElement("img")
        card.setAttribute("class", "cards")
        card.setAttribute("src", "cards/back.png")
        document.getElementById("player").append(card)
    })

    dealer.forEach(() => {
        let card = document.createElement("img")
        card.setAttribute("class", "cards")
        card.setAttribute("src", "cards/back.png")
        document.getElementById("dealer").append(card)
    })

    const start = () => {

        if((document.getElementById("bet").value) > balance) {
            dealer = [d1,d2]
            player = [p1,p2]

            document.getElementById("dtotal").textContent = "Dealer Total: "
            document.getElementById("ptotal").textContent = "Player Total: "

            document.getElementById("title").textContent = "NOT ENOUGH MONEY!"
            document.getElementById("title").setAttribute("style", "color:white")
            player.forEach(() => {
                let card = document.createElement("img")
                card.setAttribute("class", "cards")
                card.setAttribute("src", "cards/back.png")
                document.getElementById("player").append(card)
            })
        
            dealer.forEach(() => {
                let card = document.createElement("img")
                card.setAttribute("class", "cards")
                card.setAttribute("src", "cards/back.png")
                document.getElementById("dealer").append(card)
            })
        } else { 

            betamount = document.getElementById("bet").value
            balance = (parseInt(balance) - parseInt(betamount))
            updatebalance()

            document.getElementById("hit").disabled = false
            document.getElementById("stand").disabled = false
            document.getElementById("double").disabled = false
            document.getElementById("restart").disabled = true
            document.getElementById("bet").disabled = true

            // Create Hands
            d1 = Math.floor(Math.random() * 13 + 1)
            d2 = Math.floor(Math.random() * 13 + 1)
            d3 = 0
            p1 = Math.floor(Math.random() * 13 + 1)
            p2 = Math.floor(Math.random() * 13 + 1)
            p3 = 0
            
            dealer = [d1,d2]
            player = [p1,p2]

            let card = document.createElement("img")
            card.setAttribute("class", "cards")
            card.setAttribute("src", "cards/"+d1+".png")
            document.getElementById("dealer").append(card)

            let back = document.createElement("img")
            back.setAttribute("class", "cards")
            back.setAttribute("src", "cards/back.png")
            back.setAttribute("id", "facedown")
            document.getElementById("dealer").append(back)


            
            player.forEach((player) => {
                let card = document.createElement("img")
                card.setAttribute("class", "cards")
                card.setAttribute("src", "cards/"+player+".png")
                document.getElementById("player").append(card)
            })

            for (let i = 0; i < player.length; i++) {
                if((player[i]==11)||(player[i]==12)||(player[i]==13)){
                    player[i] = 10
                }
            }
            
            for (let i = 0; i < dealer.length; i++) {
            if((dealer[i]==11)||(dealer[i]==12)||(dealer[i]==13)){
                dealer[i] = 10
            }
            }

            total = 0
            acetotal = 0

            total = player.reduce((partialSum, a) => partialSum + a, 0)
            pfinal = total
            document.getElementById("ptotal").textContent = "Player Total: " + total
            for (let i = 0; i < player.length; i++) {
                if(1==player[i]){
                    playerace = []
                    player.forEach((card) => {
                        playerace.push(card)
                    })
                    playerace[i] = 11
                    acetotal = playerace.reduce((partialSum, a) => partialSum + a, 0)
                    if(acetotal < 22){
                        document.getElementById("ptotal").textContent = "Player Total: " + total + ", " + acetotal
                        pfinal = acetotal
                    }
                } 
            }

            dtotal = 0
            dacetotal = 0

            document.getElementById("dtotal").textContent = "Dealer Total: " + dealer[0]
            if(dealer[0] == 1){
                document.getElementById("dtotal").textContent = "Dealer Total: " + dealer[0] + ", 11"
            }
        }
}

// CONST REDUCE
const reduce = (person) => {
    for (let i = 0; i < person.length; i++) {
        if((person[i]==11)||(person[i]==12)||(person[i]==13)){
            person[i] = 10
        }
      }
}
// CONST PLAYER UPDATE POINTS
const updateP = () => {
    total = player.reduce((partialSum, a) => partialSum + a, 0)
    pfinal = total
    document.getElementById("ptotal").textContent = "Player Total: " + total
    for (let i = 0; i < player.length; i++) {
        if(1==player[i]){
            playerace = []
            player.forEach((card) => {
                playerace.push(card)
            })
            playerace[i] = 11
            acetotal = playerace.reduce((partialSum, a) => partialSum + a, 0)
            if(acetotal < 22){
                document.getElementById("ptotal").textContent = "Player Total: " + total + ", " + acetotal
                pfinal = acetotal
            }
        } 
      }

}

// CONST DEALER UPDATE POINTS
const updateD = () => {
    dtotal = dealer.reduce((partialSum, a) => partialSum + a, 0)
    dfinal = dtotal
    document.getElementById("dtotal").textContent = "Dealer Total: " + dtotal
    for (let i = 0; i < dealer.length; i++) {
        if(1==dealer[i]){
            dealerace = []
            dealer.forEach((card) => {
                dealerace.push(card)
            })
            dealerace[i] = 11
            dacetotal = dealerace.reduce((partialSum, a) => partialSum + a, 0)
            if(dacetotal < 22){
                document.getElementById("dtotal").textContent = "Dealer Total: " + dtotal + ", " + dacetotal
                dfinal = dacetotal
            }
        } 
      }
}

// CONST DEALER HIT
const hit = () => {
        d3 = Math.floor(Math.random() * 13 + 1)
        dealer.push(d3)
        let card = document.createElement("img")
        card.setAttribute("class", "cards")
        card.setAttribute("src", "cards/"+d3+".png")
        document.getElementById("dealer").append(card)
        reduce(dealer)
        updateD()
    }


// CONST PLAYER HIT

const phit = () => {
        p3 = Math.floor(Math.random() * 13 + 1)
        player.push(p3)
        let card = document.createElement("img")
        card.setAttribute("class", "cards")
        card.setAttribute("src", "cards/"+p3+".png")
        document.getElementById("player").append(card)
        reduce(player)
        updateP()
        if(pfinal > 21){
            document.getElementById("hit").disabled = true
            document.getElementById("stand").disabled = true  
             document.getElementById("double").disabled = true
             document.getElementById("restart").disabled = false
             document.getElementById("bet").disabled = false
            document.getElementById("title").textContent = "BUST!"
            document.getElementById("title").setAttribute("style", "color:red")
        }
        
        document.getElementById("double").disabled = true
}

    document.getElementById("hit").addEventListener("click", function(){
        phit()
    })

// CONST WIN AND LOSE AMOUNTS

const win = () => {
    betamount = document.getElementById("bet").value
    balance = (parseInt(balance) + parseInt(betamount)+ parseInt(betamount))
    updatebalance()
}

// STAND

const stand = () => {
        document.getElementById("hit").disabled = true
        document.getElementById("stand").disabled = true
        document.getElementById("double").disabled = true
        document.getElementById("restart").disabled = false
        document.getElementById("bet").disabled = false
        document.getElementById("dealer").removeChild(document.getElementById("facedown"))
        let back = document.createElement("img")
        back.setAttribute("class", "cards")
        back.setAttribute("src", "cards/"+d2+".png")
        back.setAttribute("id", "facedown")
        document.getElementById("dealer").append(back)
        updateD()
        while(dfinal < 17){
            hit()
        }
        if(dfinal > 21){
            document.getElementById("title").textContent = "WIN!"
            document.getElementById("title").setAttribute("style", "color:lime")
            win()
        } else {
// COMPARE THE POINTS
            if(dfinal > pfinal){
                document.getElementById("title").textContent = "LOSE!"
                document.getElementById("title").setAttribute("style", "color:red")
            } else if (pfinal > dfinal){
                document.getElementById("title").textContent = "WIN!"
                document.getElementById("title").setAttribute("style", "color:lime") 
                win()
            } else {
                document.getElementById("title").textContent = "DRAW!"
                balance = (parseInt(balance) + parseInt(betamount))
                updatebalance()
                document.getElementById("title").setAttribute("style", "color:white")
            }
        }
}

    document.getElementById("stand").addEventListener("click", function() {
        stand()
    })

// DOUBLE

    document.getElementById("double").addEventListener("click", function() {
        betamount = document.getElementById("bet").value
        if((betamount) > balance){
            document.getElementById("title").textContent = "NOT ENOUGH MONEY!"
            document.getElementById("title").setAttribute("style", "color:white")
        } else {
            phit()
            if(pfinal > 21){
                balance = (parseInt(balance) - parseInt(betamount))
                updatebalance()
            }
            if(pfinal < 22){
                stand()
                if(dfinal > 21){
                    balance = (parseInt(balance) + parseInt(betamount))
                    updatebalance()
                } else {
        // COMPARE THE POINTS
                    if(dfinal > pfinal){
                        balance = (parseInt(balance) - parseInt(betamount))
                        updatebalance()
                    } else if (pfinal > dfinal){
                        balance = (parseInt(balance) + parseInt(betamount))
                        updatebalance()
                    }
                }
            }
        }
    })

    // PLAY AGAIN BUTTON

    document.getElementById("restart").addEventListener("click", function() {
        betamount = document.getElementById("bet").value
        if(betamount == 80085){
            balance = 1000000000
            updatebalance()
            document.getElementById("bet").value = 0
        } else {
            document.getElementById("title").textContent = "BLACKJACK"
        document.getElementById("title").setAttribute("style", "color:white") 
        var images = document.getElementsByTagName('img');
        while (images.length > 1) {
            images[1].parentNode.removeChild(images[1]);
        }
        start()
        }
    })
}) 