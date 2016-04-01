var domain = document.domain;
var latencies = [];

jQuery(function($){

  if (!('WebSocket' in window)) {
    console.log('Your browser does not support web sockets');
  }else{
  	console.log('Setting up websocket.');
    setup();
  }

  function setup(){
   
    // Note: You have to change the host var 
    // if your client runs on a different machine than the websocket server

    var host = 'ws://' + domain + ':4000';
    var socket = new WebSocket(host);
    //console.log('socket status: ' + socket.readyState);   
    
    var $txt = $('.data');
    var $btnSend = $('.sendtext');

    $txt.focus();

    // event handlers for UI
    $btnSend.on('click',function(){
      var text = $txt.val();
      if(text == ''){
        return;
      }
      // Check text for client commands
      if (text.match("^\\+")) {
        executeClientCommand(text.substring(1));
      }
      else {
        socket.send(text);        
      }
      $txt.val('');    
    });

    $txt.keypress(function(evt){
      if(evt.which == 13){
        $btnSend.click();
      }
    });

    if (Gamepad) {
      var myGamepad = Object.create(Gamepad).init();
      myGamepad.buttons.ddown.onStart = function () {
        $txt.val('south');
        $btnSend.click();
      }
      myGamepad.buttons.dup.onStart = function () {
        $txt.val('north');
        $btnSend.click();
      }
      myGamepad.buttons.dleft.onStart = function () {
        $txt.val('west');
        $btnSend.click();
      }
      myGamepad.buttons.dright.onStart = function () {
        $txt.val('east');
        $btnSend.click();
      }
      function step() {
        myGamepad.update(1);
        window.requestAnimationFrame(step);
      }
      step();
    }

    // event handlers for websocket
    if(socket){

      socket.onopen = function(){
      	socket.send( player_id );
      }

      socket.onmessage = function(msg){
        showServerResponse(msg.data);
      }

      socket.onclose = function(){
        //alert('connection closed....');
        showServerResponse('The connection has been closed.');
      }

    }else{
      console.log('invalid socket');
    }

    setKeyboardListeners();

  }
});

function showServerResponse(data) {
  console.log('SERVER: ' + data);
  var txt = '';
  var richData = false;
  try {
    data = JSON.parse(data); 
    txt = data.message;
    richData = true
  }
  catch(err) {
    txt = data;
  }

  // If there's richData, use it
  if ( richData ) {

    var d = new Date();
    var serverDate = new Date(data.time);
    var shortTime = serverDate.getHours() + ':' + (serverDate.getMinutes()<10?'0':'') + serverDate.getMinutes() + ':' + (serverDate.getSeconds()<10?'0':'') + serverDate.getSeconds();
    var longTime = 'Last Sync: ' + serverDate.getHours() + ':' + (serverDate.getMinutes()<10?'0':'') + serverDate.getMinutes() + ':' + serverDate.getSeconds() + ':' + serverDate.getMilliseconds();

    $('.last-sync').html( longTime );

    if ( latencies.length > 5 ) {
      latencies.shift();
    }
    latencies.push(d - serverDate);

    if( latencies.length > 0 ) {
      var currentLatency = 0;
      for( var i = 0; i < latencies.length; i++ ) {
        currentLatency += latencies[i];
      }
      currentLatency = Math.round( currentLatency / latencies.length );
    }

    $('.latency').html('Latency (last five requests): ' + currentLatency + 'ms' );

    // Room
    $('.room-name').html( data.room.title );
    $('.room-desc').html( data.room.desc );

    $('.room > ul').empty();
    $.each(data.room.mobiles, function(key, value) {
      $('.room > ul').append('<li>' + value + '</li>');
    });
    $('.room > ul').append('<br>');
    $.each(data.room.items, function(key, value) {
      $('.room > ul').append('<li>' + value + '</li>');
    });

    // Player
    $('.player-name').html ( data.player.name );

    $('.hpinterior').width( ( data.player.hp / data.player.maxhp * 100 ) + '%' );
    $('.hp').html( data.player.hp + '/' + data.player.maxhp + 'hp');

    $('.player-combo').html( data.player.charRace + ' ' + data.player.charClass );

    // Info Panels
    $('.inventory > ul').empty();
    $.each(data.inventory, function(key, value) {
      $('.inventory > ul').append('<li>' + value + '</li>');
    });

    $('.equipment > ul').empty();
    $.each(data.equipment, function(key, value) {
      $('.equipment > ul').append('<li>&lt;' + key + '&gt; ' + value + '</li>');
    });

    $('.affects > ul').empty();
    $.each(data.affects, function(key, value) {
      $('.affects > ul').append('<li>' + key + ': ' + value + 's</li>');
    });

    $('.charges > ul > li:nth-child(-n+' + data.player.charges + ')').addClass('charged');

    $('.who > ul').empty();
    $.each(data.who, function(key, value) {
      $('.who > ul').append('<li>' + value + '</li>');
    });

    if ( data.comm ) {
      var li = document.createElement('li');
      li.innerHTML = shortTime + ': ' + txt;
      $('.comm').append(li);

      // If there are more than 50 nodes, remove the oldest node
      var commCount = $('.comm > ul > li').length;
      if ( commCount > 50 ) {
        $('.comm > ul > li:first-child').remove();
      }
    }
  }

  var li = document.createElement('li');
  // li.innerHTML = shortTime + ': ' + txt;
  li.innerHTML = txt;
  $('.output > ul').append(li); 

  // If there are more than 50 nodes, remove the oldest node
  var outputCount = $('.output > ul > li').length;
  if ( outputCount > 50 ) {
    $('.output > ul > li:first-child').remove();
  }

  $('.output').scrollTop( $('.output')[0].scrollHeight );
}

function executeClientCommand(text) {
  if (text == 'i') {
    $('.info > div:not(.inventory)').removeClass('active');
    $('.menus > div:not(.inventory-menu)').removeClass('active');
    $('.inventory').addClass('active');
    $('.inventory-menu').addClass('active');
  }
  else if (text == 'e') {
    $('.info > div:not(.equipment)').removeClass('active');
    $('.menus > div:not(.equipment-menu)').removeClass('active');
    $('.equipment').addClass('active');
    $('.equipment-menu').addClass('active'); 
  }
  else if (text == 'w') {
    $('.info > div:not(.who)').removeClass('active');
    $('.menus > div:not(.who-menu)').removeClass('active');
    $('.who').addClass('active');
    $('.who-menu').addClass('active');  
  }
  else if (text == 'c') {
    $('.info > div:not(.comm)').removeClass('active');
    $('.menus > div:not(.comm-menu)').removeClass('active');
    $('.comm').addClass('active');
    $('.comm-menu').addClass('active'); 
  }
}

function setKeyboardListeners() {
  console.log('Setting keyboard listeners.');

  shortcut.add('F1', function() {
    executeClientCommand('i');
  });
  
  shortcut.add('F2', function() {
    executeClientCommand('e');
  });
  
  shortcut.add('F3', function() {
    executeClientCommand('c');
  });
  
  shortcut.add('F4', function() {
    executeClientCommand('w');
  });
}