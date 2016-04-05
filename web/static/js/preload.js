function sleep(milliseconds) {
  var start = new Date().getTime();
  for (var i = 0; i < 1e7; i++) {
    if ((new Date().getTime() - start) > milliseconds){
      break;
    }
  }
}

function preloadAssets() {
  console.log('Loading assets.');
  var startTime = new Date();

  var mediaArray = [];
  var iconArray = [];

  preloadMedia = "temple.jpg".split(',');
  preloadIcons = "awareness.png,battle-gear.png,blindfold.png,conversation.png,knapsack.png,pyromaniac.png,sly.png".split(',');

  for(var x=0;x<preloadMedia.length;x++) {
    mediaArray[x] = new Image();
    mediaArray[x].src = '../static/media/' + preloadMedia[x];
  }

  for(var x=0;x<preloadIcons.length;x++) {
    iconArray[x] = new Image();
    iconArray[x].src = '../static/media/icons/' + preloadIcons[x];
  }

  var endTime = new Date();
  console.log('All assets loaded. Duration: ' + ( endTime - startTime ) + 'ms.');
}

preloadAssets();