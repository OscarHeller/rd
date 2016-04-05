var domain = document.domain;
var latencies = [];

var commandHistory = [];
var historyPointer = 0;

jQuery(function($){

  if (!('WebSocket' in window)) {
    console.log('Your browser does not support websockets.');
  }else{
  	console.log('Setting up websocket.');
    setup();
  }

  function setup(){   
    // Note: You have to change the host var 
    // if your client runs on a different machine than the websocket server

    var host = 'ws://' + domain + ':4000';
    var socket = new WebSocket(host);
    
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
        historyPointer = 0;
        commandHistory.unshift(text);
        socket.send(text);        
      }
      $txt.val('');    
    });

    $txt.keydown(function(evt){
      if(evt.which == 13){
        $btnSend.click();
      } else if (evt.which == 38) {
        $('.data').val(commandHistory[historyPointer]).focus();
        historyPointer = (historyPointer + 1) % commandHistory.length;
      } else if (evt.which == 27) {
        $('.data').val("");
        historyPointer = 0;
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
      console.log('Invalid socket.');
    }

    setKeyboardListeners();
    setClickListeners();

  }
});

function showServerResponse(data) {
  try {
    data = JSON.parse(data);
    console.log(data);
    parseServerResponse(data);
  }
  catch(err) {
    console.log('Server response: ' + err);
  }
}

function parseServerResponse(data) {
  // Time
  if( data.hasOwnProperty('time') ) {
    var serverDate = new Date(data.time);
    var d = new Date();
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

    console.log('Latency (last five requests): ' + currentLatency + 'ms' );
  }

  // Room
  if( data.hasOwnProperty('room') ) {
    if ( data.room.hasOwnProperty('title') ) {
      $('.room-name').html( data.room.title );
    }
    if ( data.room.hasOwnProperty('desc') ) {
      $('.room-desc').html( data.room.desc );
    }

    if ( data.room.hasOwnProperty('bg') && data.room.bg ) {
      console.log('Background image found: ' + data.room.bg);
      $('body').css({'background-image': 'url(' + data.room.bg + ')' });
    }

    if ( data.room.hasOwnProperty('mobiles') ) {
      $('.room > .room-info > ul').empty();
      $.each(data.room.mobiles, function(key, value) {
        $('.room > .room-info > ul').append('<li>' + value + '</li>');
      });
    }

    if ( data.room.hasOwnProperty('items') ) {
      $('.room > .room-info > ul').append('<br>');
      $.each(data.room.items, function(key, value) {
        $('.room > .room-info > ul').append('<li>' + value + '</li>');
      });
    }
  }

  // Player
  if( data.hasOwnProperty('player') ) {
    if( data.player.hasOwnProperty('name') ) {
      $('.player-name').html ( data.player.name );
    }
    if( data.player.hasOwnProperty('hp') && data.player.hasOwnProperty('maxhp') ) {
      $('.hpinterior').css('width', ( data.player.hp / data.player.maxhp * 100 ) + '%' );
      $('.hp').html( data.player.hp + '/' + data.player.maxhp + 'hp');
    }

    if( data.player.hasOwnProperty('charRace') && data.player.hasOwnProperty('charClass') ) {
      $('.player-combo').html( data.player.charRace + ' ' + data.player.charClass );
    }

    if( data.player.hasOwnProperty('charges') ) {
      $('.charges > ul > li').removeClass('charged');
      $('.charges > ul > li:nth-child(-n+' + data.player.charges + ')').addClass('charged');
    }
  }

  // Info Panels
  if( data.hasOwnProperty('craft') ) {
    $('.craft > ul').empty();
    $.each(data.craft, function(key, value) {
      var buf = '<li><h2>' + key + '</h2><ul>';

      $.each(value, function(key, value) {
        buf += '<li>' + value.count + ': ' + value.name + '</li>';
      });
      buf += '</ul></li>';
      $('.craft > ul').append(buf);
    });
  }

  if( data.hasOwnProperty('commands') ) {
    $('.commands > ul').empty();
    $.each(data.commands, function(key, value) {
      $('.commands > ul').append('<li>' + value + '</li>');
    });
  }

  if( data.hasOwnProperty('score') ) {
    $('.score > ul').empty();
    $.each(data.score, function(key, value) {
      $('.score > ul').append('<li>' + key + ': ' + value + '</li>');
    });
  }

  if( data.hasOwnProperty('inventory') ) {
    $('.inventory > ul').empty();
    $.each(data.inventory, function(key, value) {
      $('.inventory > ul').append('<li>' + value + '</li>');
    });
  }

  if( data.hasOwnProperty('equipment') ) {
    $('.equipment > ul').empty();
    $.each(data.equipment, function(key, value) {
      $('.equipment > ul').append('<li>&lt;' + key + '&gt; ' + value + '</li>');
    });
  }

  if( data.hasOwnProperty('affects') ) {
    $('.affects > ul').empty();
    $.each(data.affects, function(key, value) {
      $('.affects > ul').append('<li class="affect affect-name-' + key + ' affect-friendly-' + value.friendly + '"><span>' + value.duration + 's</span></li>');
    });
  }

  if( data.hasOwnProperty('who') ) {
    $('.who > ul').empty();
    $.each(data.who, function(key, value) {
      $('.who > ul').append('<li>' + value + '</li>');
    });
  }

  if ( data.hasOwnProperty('message') ) {

    var li = document.createElement('li');
    li.innerHTML = data.message;
    $('.output > ul').append(li); 

    // If there are more than 50 nodes, remove the oldest node
    var outputCount = $('.output > ul > li').length;
    if ( outputCount > 50 ) {
      $('.output > ul > li:first-child').remove();
    }

    $('.output').scrollTop( $('.output')[0].scrollHeight );

    if ( data.comm ) {
      var li = document.createElement('li');
      li.innerHTML = data.message;
      $('.comm').append(li);

      // If there are more than 50 nodes, remove the oldest node
      var commCount = $('.comm > ul > li').length;
      if ( commCount > 50 ) {
        $('.comm > ul > li:first-child').remove();
      }
    }
  }
}

function executeClientCommand(text) {
  if (text == 'i') {
    setActiveMenu('inventory');
  }
  else if (text == 'e') {
    setActiveMenu('equipment');
  }
  else if (text == 'w') {
    setActiveMenu('who');
  }
  else if (text == 'c') {
    setActiveMenu('comm');
  }
  else if (text == 'r') {
    setActiveMenu('craft');
  }
  else if (text == 's') {
    setActiveMenu('score');
  }
  else if (text == 'm') {
    setActiveMenu('commands');
  }
}

function setActiveMenu(text) {
    $('.info-panels > div:not(.' + text + ')').removeClass('active');
    $('.menus > div:not(.' + text + '-menu)').removeClass('active');
    $('.' + text + '').addClass('active');
    $('.' + text + '-menu').addClass('active');
}

function setKeyboardListeners() {
  console.log('Setting keyboard listeners.');

  shortcut.add('F1', function() {
    setActiveMenu('who');
  });
  
  shortcut.add('F2', function() {
    setActiveMenu('inventory');
  });
  
  shortcut.add('F3', function() {
    setActiveMenu('equipment');
  });
  
  shortcut.add('F4', function() {
    setActiveMenu('comm');
  });
  
  shortcut.add('F5', function() {
    setActiveMenu('craft');
  });
  
  shortcut.add('F6', function() {
    setActiveMenu('commands');
  });
  
  shortcut.add('F7', function() {
    setActiveMenu('score');
  });
}

function setClickListeners() {
  console.log('Setting click listeners.');

  $('.inventory-menu').click(function() {
    setActiveMenu('inventory');
  });

  $('.equipment-menu').click(function() {
    setActiveMenu('equipment');
  });

  $('.who-menu').click(function() {
    setActiveMenu('who');
  });

  $('.comm-menu').click(function() {
    setActiveMenu('comm');
  });

  $('.craft-menu').click(function() {
    setActiveMenu('craft');
  });

  $('.commands-menu').click(function() {
    setActiveMenu('commands');
  });

  $('.score-menu').click(function() {
    setActiveMenu('score');
  });
}