let abortController;

// handling llm api request 
async function getResponse(formData) {
    abortController = new AbortController()


    const response = await fetch("/process", {
        method: "POST",
        body: formData,
        signal: abortController.signal
    });

    const data = await response.json();
    return data




}
const completionLoader = async function (queryValue) {
    try {
        const formData = new FormData();
        formData.append('userQuery', queryValue)
        const data = await getResponse(formData);
        return data
    } catch (error) {
        console.log(`error at fetch ${error}`)
        return { output: 'Error recorded' }

    }
}

// defining some variables 
const display = document.getElementById("display")
const input = document.getElementById('input')
const queryBox = document.querySelector('#queryBox');
const mainDisplay = document.querySelector('.mainDisplay');
const templateDisplay = document.querySelector('.templateDisplay');
const qcBaseDisplay = document.querySelector('.qcBaseDisplay')
const navBar = document.querySelector(".navBar");
const submitBtn = document.getElementById("submitBtn");
const mennu = document.getElementById("mennu")
const newChat = document.getElementById("newChat")
const queryCompletion = document.querySelector('.queryCompletion')
const sampleQueries = document.getElementById('sampleQueries')
const mennuContent = document.getElementById('mennuContent')
const mennuContentClose = document.getElementById("mennuContentClose")
const currentSessionScroll = document.querySelector(".current .sessionScroll")
const todaySessionScroll = document.querySelector(".today .sessionScroll")
const lastWeekSessionScroll = document.querySelector(".lastWeek .sessionScroll")
const othersSessionScroll = document.querySelector(".others .sessionScroll")
const addExist = document.getElementById("addExist")
const newSess = document.getElementById("newSess")

// stimulate mouse click event 
var clickEvent = new MouseEvent('click', {
    bubbles: true,
    cancelable: true,
    view: window
});


// setting inital height of the mainDisplay 
mainDisplay.style.height = `${parseInt(window.innerHeight) - parseInt(queryBox.clientHeight) - parseInt(navBar.clientHeight) - 20}px`


function adjustQueryBoxHeight() {
    const scrollHeight = queryBox.scrollHeight;
    const contentHeight = queryBox.clientHeight; // 45vh of the viewport height
    const thresholdHeight = (40 * window.innerHeight) / 100
    if (scrollHeight <= thresholdHeight) {
        queryBox.style.minHeight = Math.max(scrollHeight, contentHeight) + "px";
    } else { queryBox.style.minHeight = `${thresholdHeight}px` }
}

// adhusting queryBox height 
queryBox.addEventListener('scroll', adjustQueryBoxHeight)


function adjustMainDisplayHeight() {
    let displayHeight;
    if (window.innerWidth > 500) {
        displayHeight = parseInt(window.innerHeight) - parseInt(queryBox.clientHeight) - parseInt(navBar.clientHeight) - 20

    } else {
        displayHeight = parseInt(window.innerHeight) - parseInt(queryBox.clientHeight) - parseInt(navBar.clientHeight) + 130

    }
    mainDisplay.style.maxHeight = `${displayHeight}px`
    // console.log(`these is somthinh new ${mainDisplay.style.height}`)


}

// adjusting mainDisplay height with respect to queryBox height 
queryBox.addEventListener('scroll', adjustMainDisplayHeight)

// handling prompt completion display 
function baseHtmlCreationTemplate() {
    let queryCompletion = document.createElement('div');
    queryCompletion.innerHTML = '<div class = "query"><p class = "boldFont secondaryTxtColor textFont">You</p><p class = "userQuery secondaryTxtColor textFont "></p></div>  <div class = "completion"><p class = "boldFont secondaryTxtColor textFont">PDF Insight</p><p class = "llmCompletion secondaryTxtColor textFont"></p></div> <div class="lds-ellipsis"><div></div><div></div><div></div><div></div></div> <div class = "verticalLine"></div>'
    queryCompletion.setAttribute('class', 'queryCompletion displayFlex flexDirectionCol bottomMargin ')
    return queryCompletion
}

function promptCompletionHtmlTemplate({ ele = "", queryValue = "", llmValue = "", flagValue = "b" }) {

    let userQuery = ele.children[0].children[1]
    let llmCompletion = ele.children[1].children[1]
    if (flagValue == 'q') {
        userQuery.textContent = queryValue
    } else if (flagValue == 'c') {
        // console.log(llmCompletion)
        llmCompletion.textContent = llmValue
    } else if (flagValue == 'b') {
        userQuery.textContent = queryValue
        llmCompletion.textContent = llmValue

    }
}

function fitHtmlTemplate(baseEle, appendEle) {
    baseEle.append(appendEle)

}


// show the Loader 
function showLoader(ele) {
    let animLoader = ele.children[2];
    // console.log(animLoader)
    animLoader.style.display = 'block'

}

// hide the loader 
function hideLoader(ele) {
    let animLoader = ele.children[2];
    // console.log(animLoader)
    animLoader.style.display = 'none'

}

// show the templateDisplay 
function showTemplateDisplay() {
    templateDisplay.classList.remove('displayNone')
}

// hide the templateDisplay 
function hideTemplateDisplay() {
    templateDisplay.classList.add('displayNone')
}


// remove the query completion content 
function removeQcDisplayContent() {
    if (mainDisplay.children.length > 1) {
        mainDisplay.children[1].innerHTML = ""
    }
}

// remove query text 
function removeQueryText() {
    queryBox.value = ""
    // console.log(`inside a needed ${queryBox.value}`)
}

// add query text 
function addQueryText(userQuery) {
    queryBox.value = userQuery
    // console.log(`inside a needed ${queryBox.value}`)
}

// handling the submit button logic
submitBtn.addEventListener('click', async function () {

    hideTemplateDisplay()
    const query = queryBox.value;
    const queryCompletion = baseHtmlCreationTemplate()
    fitHtmlTemplate(baseEle = qcBaseDisplay, appendEle = queryCompletion)
    promptCompletionHtmlTemplate({ ele: queryCompletion, queryValue: query, flagValue: 'q' })
    showLoader(ele = queryCompletion)
    removeQueryText()
    const completion = await completionLoader(query)
    console.log(`query value ${query}`)
    console.log(`completion value ${completion.output}`)
    hideLoader(ele = queryCompletion)
    promptCompletionHtmlTemplate({ ele: queryCompletion, llmValue: completion.answer, flagValue: 'c' })

    if (completion.answer != "Internal Error" || completion.answer != "") {
        const data = await fetch('/userChatData', {
            method: "POST",
        })
        console.log(data)

    }
})

function sessionScrollHtmlTemplate(sessionId, sessionName, sessionDesc) {
    const div = document.createElement('div');
    div.setAttribute('class', 'mainBgColor displayFlex flexDirectionCol topPad bottomPad')
    div.setAttribute('data-session-id', sessionId)
    div.innerHTML = `<div class="displayFlex justifySpaceBtw alignItmCenter">
    <p class="secondaryTxtColor textFont normalFont pointerCursor">${sessionName}</p>
    <img src="/static/expand.svg" alt="expand" class="invert smallIconSize pointerCursor">
</div>
<div class="smallVerticalLine "></div>
<p class="displayNone secondaryTxtColor smallTextFont normalFont">${sessionDesc}</p>`
    return div

}

async function mainSessionLogicExecutor(timePeriod, baseEle) {
    if (timePeriod.length > 0) {
        timePeriod.forEach((session) => {
            const ele = sessionScrollHtmlTemplate(sessionId = session['sessionId'], sessionName = session['sessionName'], sessionDesc = session['sessionDesc'])
            ele.children[0].children[1].addEventListener('click', function (event) {
                event.stopPropagation()
                // console.log('current session is clicked')
                ele.children[2].classList.toggle('displayNone')

            })
            ele.children[0].children[0].addEventListener('click', async function (event) {
                event.stopPropagation()
                console.log('we will handle it later')
                const sessionId = session['sessionId']
                const formData = new FormData()
                formData.append('sessionId', sessionId)
                const response = await fetch('/sessionChatHistory', {
                    method: "POST",
                    body: formData
                })
                const data = await response.json()
                console.log('for chat histroy')
                console.log(data)
                // qcBaseDisplay.innerHTML = ""
                // remove any previous content that is available 
                removeQueryText()
                removeQcDisplayContent()
                if (data['userChatHistory'][0]['userQuery'] == "no chatHistory retrieved") {
                    showTemplateDisplay()
                } else {
                    hideTemplateDisplay()
                    data['userChatHistory'].forEach((chat) => {
                        const userQuery = chat['userQuery']
                        const answer = chat['answer']
                        const queryCompletion = baseHtmlCreationTemplate()
                        fitHtmlTemplate(baseEle = qcBaseDisplay, appendEle = queryCompletion)
                        promptCompletionHtmlTemplate({ 'ele': queryCompletion, 'queryValue': userQuery, 'llmValue': answer, 'flagValue': 'b' })


                    })
                }

                mennuContent.classList.toggle('displayNone')
                mennuContent.classList.toggle('displayFlex')
                display.classList.toggle('disableScreen')
                input.classList.toggle('disableScreen')



                // mennuContent.classList.toggle('displayNone')
                // mennuContent.classList.toggle('displayFlex')
            })
            fitHtmlTemplate(baseEle = baseEle, appendEle = ele)



        })

    }
    else {
        baseEle.innerHTML = '<p class="secondaryTxtColor textFont normalFont pointerCursor">Empty</p>'
    }
}

// automatically trigger the click event when chat html starts
window.addEventListener('DOMContentLoaded', function () {
    mennu.click();
})


// handling the mennu 
mennu.addEventListener('click', async function () {
    console.log('mennu is clicked and changed')
    mennuContent.classList.toggle('displayNone')
    mennuContent.classList.toggle('displayFlex')
    display.classList.toggle('disableScreen')
    input.classList.toggle('disableScreen')

    const response = await fetch('/userAllSessions', {
        method: "POST",
    })
    const data = await response.json()
    // return jsonify({'current': current, 'today': today, 'lastWeek': lastWeek, 'others': others})
    const current = data.current
    const today = data.today
    const lastWeek = data.lastWeek
    const others = data.others
    console.log('current')
    console.log(current)
    console.log('today')
    console.log(today)
    console.log('lastWeek')
    console.log(lastWeek)
    console.log('others')
    console.log(others)

    // current handling
    currentSessionScroll.innerHTML = ""
    mainSessionLogicExecutor(timePeriod = current, baseEle = currentSessionScroll)
    // if (current.length > 0) {
    //     const ele = sessionScrollHtmlTemplate(sessionId = current[0]['sessionId'], sessionName = current[0]['sessionName'], sessionDesc = current[0]['sessionDesc'])
    //     ele.children[0].children[1].addEventListener('click', function (event) {
    //         event.stopPropagation()
    //         console.log('current session is clicked')
    //         ele.children[2].classList.toggle('displayNone')

    //     })
    //     ele.children[0].children[0].addEventListener('click', async function (event) {
    //         event.stopPropagation()
    //         const formData = new FormData();
    //         formData.append('sessionId', current[0]['sessionId'])
    //         const response = await fetch('/sessionChatHistory', {
    //             method: "POST",
    //             body: formData
    //         })
    //         const data = await response.json()
    //         console.log('for chat histroy')
    //         console.log(data)
    //         // qcBaseDisplay.innerHTML = ""
    //         // remove any previous content that is available 
    //         removeQueryText()
    //         removeQcDisplayContent()
    //         if (data['userChatHistory'][0]['userQuery'] == "no chatHistory retrieved") {
    //             showTemplateDisplay()
    //         } else {
    //             hideTemplateDisplay()
    //             data['userChatHistory'].forEach((chat) => {
    //                 const userQuery = chat['userQuery']
    //                 const answer = chat['answer']
    //                 const queryCompletion = baseHtmlCreationTemplate()
    //                 fitHtmlTemplate(baseEle = qcBaseDisplay, appendEle = queryCompletion)
    //                 promptCompletionHtmlTemplate({ 'ele': queryCompletion, 'queryValue': userQuery, 'llmValue': answer, 'flagValue': 'b' })


    //             })
    //         }

    //         mennuContent.classList.toggle('displayNone')
    //         mennuContent.classList.toggle('displayFlex')
    //         display.classList.toggle('disableScreen')
    //         input.classList.toggle('disableScreen')


    //     })
    //     fitHtmlTemplate(baseEle = currentSessionScroll, appendEle = ele)
    // }



    // today handling
    todaySessionScroll.innerHTML = ""
    mainSessionLogicExecutor(timePeriod = today, baseEle = todaySessionScroll)


    // lastWeek handling
    lastWeekSessionScroll.innerHTML = ""
    mainSessionLogicExecutor(timePeriod = lastWeek, baseEle = lastWeekSessionScroll)



    // others handling  
    othersSessionScroll.innerHTML = ""
    mainSessionLogicExecutor(timePeriod = others, baseEle = othersSessionScroll)



    console.log(data)
    console.log(currentSessionScroll)


    // option button handling
    if (current.length == 0) {
        addExist.classList.add('displayNone')
    } else {
        addExist.classList.remove('displayNone')

    }

    addExist.addEventListener('click', async function () {
        const formData = new FormData();
        formData.append('status', 'e')
        await fetch('/status',
            {
                method: "POST",
                body: formData
            }
        )
        window.location.href = '/reDirect/uploadUi'
    })

    newSess.addEventListener('click', async function () {
        const formData = new FormData();
        formData.append('status', 'n')
        await fetch('/status',
            {
                method: "POST",
                body: formData
            }
        )
        window.location.href = '/reDirect/uploadUi'

    })




})

mennuContentClose.addEventListener('click', function () {
    mennuContent.classList.toggle('displayNone')
    mennuContent.classList.toggle('displayFlex')
    display.classList.toggle('disableScreen')
    input.classList.toggle('disableScreen')
})



// handling the new chat logic 
newChat.addEventListener('click', function () {
    // checking whether the abortController is defined or not 
    if (abortController) {
        abortController.abort()
    }
    removeQueryText()
    removeQcDisplayContent()
    showTemplateDisplay()




})

// handling the sample query language 
const samples = Array.from(sampleQueries.children)
for (const sampleIndex in samples) {
    samples[sampleIndex].addEventListener('click', function () {
        let query = samples[sampleIndex].textContent
        query = query.replace(/\s+/g, ' ');
        addQueryText(query)
        submitBtn.dispatchEvent(clickEvent)



    })

}


