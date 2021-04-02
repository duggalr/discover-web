
chrome.runtime.onInstalled.addListener( () => {

});


chrome.contextMenus.create({
  "id": "text_snippet",
  "title": "Save Text",
  "contexts": ["selection"]
});


chrome.contextMenus.onClicked.addListener(async function(info, tab){
  var selectedText = info.selectionText
  var tabUrl = tab.url
  var tabTitle = tab.title
  jsonRV = {
    'tabURL': tabUrl, 'tabTitle': tabTitle, 'selectedText': selectedText
  }
  console.log('Selected text: ' + selectedText + ' from tab: '+ tabUrl);
  // console.log(JSON.stringify(jsonRV));
  var serverRV = await sendText(JSON.stringify(jsonRV))
  console.log('server:', serverRV)
});


function sendText(jsonRV) {
var url = 'http://127.0.0.1:8000/save_text'
return new Promise((res, rej) => {
    fetch(url, {
      method: 'POST',
      headers: {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
      },
      body: jsonRV
      }).then(function(response) {
      response.json().then(function(val){
        res(val)
      })
    });
  })
}





