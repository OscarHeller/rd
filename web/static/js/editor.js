var app = angular.module('map', []);
var uid = 0;
//var storage = localStorage;

var s;
app.controller('mapCtrl', function ($scope) {
  s = $scope;
  $scope.newRoom;
  $scope.newExit;
  $scope.newItem;
  $scope.newNPC;
  $("#roomDesc").jqte();

  $scope.load = function () {

    $scope.rooms = {};
    $scope.items = [];
    $scope.npcs = [];
    $scope.images = [];

    $scope.setNewRoom();
    $scope.setNewExit();
    $scope.setNewItem();
    $scope.setNewNPC();
    $scope.newItemRoomKey = "";
    $scope.newItemNPCKey = "";
    $scope.newItemKeyword = "";

    var request = new XMLHttpRequest();
    request.open('POST', '/editor', true);
    request.onload = function (data) {
      var response = angular.fromJson(request.response);

      var room_response = response['rooms'];
      var item_response = response['items'];
      var npc_response = response['npcs'];
      var image_response = response['images'];

      for (var i = 0; i < room_response.length; i++) {
        $oid = room_response[i]['_id']['$oid'];
        $scope.rooms[$oid] = room_response[i];
        $scope.rooms[$oid].id = $oid;
        if (!$scope.rooms[$oid].items) $scope.rooms[$oid].items = [];
      }

      for (var i = 0; i < item_response.length; i++) {
        $scope.items.push(item_response[i])
      }

      for (var i = 0; i < npc_response.length; i++) {
        $scope.npcs.push(npc_response[i]);
      }

      for (let i = 0; i < image_response.length; i++) {
        $scope.images.push(image_response[i]);
      }

      $scope.$digest();
    };
    request.send();
  }

  $scope.setNewRoom = function () { $scope.newRoom = {name: '', exits: {}, items: [], npcs: []}; }
  $scope.getRoom = function (exit) {
    return rooms[exit.target];
  }  
  $scope.submitRoom = function () {
    var id = $scope.newRoom.id === undefined ? ++uid : $scope.newRoom.id;
    //$scope.newRoom.description = $(".")
    //$scope.newRoom.description = $("#roomDesc").val();
    $scope.newRoom.description = $('#roomDesc').val();//.replace(/"/g, '&quot;');
    $scope.rooms[id] = $scope.newRoom;
    $scope.newRoom.id = id;
    $scope.setNewRoom();
    $scope.save();
  }
  $scope.editRoom = function (room) {
    $scope.newRoom = room;
    $("#roomDesc").jqteVal($scope.newRoom.description);
  }
  $scope.removeRoom = function (room) { 
    if (window.confirm("Are you sure you want to delete this room?")) {
      room['delete'] = 1;
    }
  }

  $scope.isDeleted = function (obj) {
    if (obj['delete'] && obj['delete'] == 1) {
      return "list-group-item-danger"
    }
  }

  $scope.setNewItem = function () {
    $scope.newItemRoomKey = "";
    $scope.newItemKeyword = "";
    $scope.newItem = {};
  }
  $scope.submitItem = function () {
    $scope.items.push($scope.newItem)
    $scope.setNewItem();
    $scope.save();
  };
  $scope.removeItem = function (item) { 
    if (window.confirm("Are you sure you want to delete this item?")) {
      item['delete'] = 1;
    }
  };
  $scope.addItemToRoom = function () {
    if (!$scope.newRoom.items) $scope.newRoom.items = [];
    $scope.newRoom.items.push($scope.newItemRoomKey);
    $scope.newItemRoomKey = "";
  }
  $scope.addNPCToRoom = function () {
    if (!$scope.newRoom.npcs) $scope.newRoom.npcs = [];
    $scope.newRoom.npcs.push($scope.newNPCKey);
    $scope.newNPCKey = "";
  }
  $scope.removeItemFromRoom = function (item) {
    var i = $scope.newRoom.items.indexOf(item);
    $scope.newRoom.items.splice(i, 1);
  }
  $scope.findItem = function (item) {
    for (var i = 0; i < $scope.items.length; i++) {
      if (item == $scope.items[i]['_id']['$oid']) {
        return $scope.items[i]['name'];
      }
    }
    return "";
  }
  $scope.findNPC = function (npc) {
    for (var i = 0; i < $scope.npcs.length; i++) {
      if (npc == $scope.npcs[i]['_id']['$oid']) {
        return $scope.npcs[i]['name'];
      }
    }
    return "";
  }

  $scope.editItem = function (item) {
    $scope.newItem = item;
  }
  $scope.addItemKeyword = function () {
    if (!$scope.newItem.keywords) $scope.newItem.keywords = [];
    $scope.newItem.keywords.push($scope.newItemKeyword);
    $scope.newItemKeyword = "";
  }
  $scope.removeItemKeyword = function (keyword) {
    var i = $scope.newItem.keywords.indexOf(keyword);
    $scope.newItem.keywords.splice(i, 1);
  }
  $scope.addItemStat = function () {
    if (!$scope.newItem.stats) $scope.newItem.stats = {};
    $scope.newItem.stats[$scope.newItemStat.field] = $scope.newItemStat.val;
    $scope.newItemStat = {};
  }
  $scope.removeItemStat = function (field) {
    delete $scope.newItem.stats[field];
  }

  $scope.setNewExit = function () { $scope.newExit = {direction: 'South', target: undefined}; };
  $scope.addExit = function () {
    $scope.newRoom.exits[$scope.newExit.direction] = $scope.newExit;
    $scope.setNewExit();
  }
  $scope.removeExit = function (exit) {
    delete($scope.newRoom.exits[exit.direction]);
  }
  $scope.addRoomStat = function () {
    if (!$scope.newRoom.stats) $scope.newRoom.stats = {};
    $scope.newRoom.stats[$scope.newRoomStat.field] = $scope.newRoomStat.val;
    $scope.newRoomStat = {};
  }
  $scope.removeRoomStat = function (field) {
    // fix me this doesn't seem to work - fix!
    delete $scope.newRoom.stats[field];
  }


  $scope.setNewNPC = function () {
    $scope.newNPC = {};
  };
  $scope.submitNPC = function () {
    $scope.npcs.push($scope.newNPC);
    $scope.setNewNPC();
    $scope.save();
  }
  $scope.removeNPC = function (npc) { 
    if (window.confirm("Are you sure you want to delete this npc?")) {
      npc['delete'] = 1;
    }
  }
  $scope.editNPC = function (npc) {
    $scope.newNPC = npc;
  };
  $scope.removeNPCFromRoom = function (npc) {
    var i = $scope.newRoom.npcs.indexOf(npc);
    $scope.newRoom.npcs.splice(i, 1);
  }
  $scope.addNPCKeyword = function () {
    if (!$scope.newNPC.keywords) $scope.newNPC.keywords = [];
    $scope.newNPC.keywords.push($scope.newNPCKeyword);
    $scope.newNPCKeyword = "";
  }
  $scope.removeNPCKeyword = function (keyword) {
    var i = $scope.newNPC.keywords.indexOf(keyword);
    $scope.newNPC.keywords.splice(i, 1);
  }
  $scope.addNPCStat = function () {
    if (!$scope.newNPC.stats) $scope.newNPC.stats = {};
    $scope.newNPC.stats[$scope.newNPCStat.field] = $scope.newNPCStat.val;
    $scope.newNPCStat = {};
  }
  $scope.removeNPCStat = function (field) {
    delete $scope.newNPC.stats[field];
  }
  $scope.addItemToNPC = function () {
    if (!$scope.newNPC.inventory) $scope.newNPC.inventory = [];
    $scope.newNPC.inventory.push($scope.newItemNPCKey);
    $scope.newItemNPCKey = "";
  }
  $scope.removeItemFromNPC = function (item) {
    var i = $scope.newNPC.inventory.indexOf(item);
    $scope.newNPC.inventory.splice(i, 1);
  }


  $scope.save = function () {
    var roomData = [];
    for (key in $scope.rooms) {
      roomData.push($scope.rooms[key]);
    }
    //var rooms = angular.toJson($scope.rooms);
    //var items = angular.toJson($scope.items);
    //var npcs = angular.toJson($scope.npcs);

    var data = {
      rooms: $scope.rooms, items: $scope.items, npcs: $scope.npcs
    };

    //var data = 'rooms=' + rooms + '&items=' + items + '&npcs=' + npcs;
    // obligatory comment so I can commit & deploy
    
    var request = new XMLHttpRequest();
    request.open('PATCH', '/editor', true);
    request.setRequestHeader("Content-type", "application/x-www-form-urlencoded");
    request.onload = function (data) {
      $scope.load();
    };
    //request.send('rooms=' + rooms + '&items=' + items + '&npcs=' + npcs );
    request.send('data=' + angular.toJson(data).replace(/;/g, "%3B"));
  };

  $scope.load();

});
  
