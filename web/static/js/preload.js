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

  bgList = bgList.split(',');
  iconList = iconList.split(',');

  for(var x=0;x<bgList.length;x++) {
    mediaArray[x] = new Image();
    mediaArray[x].src = '../static/media/' + bgList[x];
    console.log('Loaded ' + bgList[x]);
  }
  console.log('Backgrounds loaded.');

  for(var x=0;x<iconList.length;x++) {
    iconArray[x] = new Image();
    iconArray[x].src = '../static/media/icons/' + iconList[x];
    console.log('Loaded ' + iconList[x]);
  }
  console.log('Icons loaded.');

  var endTime = new Date();
  console.log('All assets loaded. Duration: ' + ( endTime - startTime ) + 'ms.');
}

if (typeof bgList !== 'undefined' && typeof iconList !== 'undefined' ) {
  preloadAssets(); 
}
else {
  console.log('Preloading failed.');
}
