

// TODO: need live listeners to constantly update database, etc.

chrome.runtime.onInstalled.addListener(() => {
  console.log('service worker works');

  //  TODO: we just want all the bookmarks from all folders; (don't need folder organization, etc)
    // get the date added as well
  chrome.bookmarks.getTree(
    function(bookmarkTreeNodes) {
      // console.log(bookmarkTreeNodes);
      var children = bookmarkTreeNodes[0]['children']
      for (i=0; i<=children.length-1; i++) {
        var li = children[i]['children']
        getBookMarks(li)
      }
    }
  );

  // Save into database
  function getBookMarks(arr) {
    for (i=0; i<=arr.length-1; i++) {
      var di = arr[i]
      var bookmark_date = di['dateAdded']  // use unix timestamp in sqlite too
      var bookmark_title = di['title']
      var bookmark_url = di['url']
      var bookmark_id = di['url']
      
      // Send off to flask API 

    }
  }

  query = {
    'text': '',
    'startTime': 1609477200, // 2021/01/01 
    'maxResults': 1000000  
  }
  chrome.history.search(query, function(results) {
    console.log('results length', results.length)
    for (i=0; i<=results.length-1; i++) {
      di = results[i]
      lastVisitedTime = di['lastVisitTime']
      visitCount = di['visitCount']
      title = di['title']
      url = di['url']
      url_id = di['id']
    }
  })
  query = {
    'url': 'https://geohot.github.io/blog/'
  }
  chrome.history.getVisits(query, function(results){ 
    console.log(results)
    for (i=0; i<=results.length-1; i++) {
      di = results[i]
      url_id = di['id']
      visit_id = di['visitId']
      referrer_visit_id = di['referringVisitId']
      visitTime = di['visitTime']
      transition_type = di['transition']
      
    }
    
  })

});




