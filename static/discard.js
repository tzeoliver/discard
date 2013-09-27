$(function() {
  var NUM_SUITS = 4
  var NUM_CARDS_PER_SUIT = 13
  var NUM_CARDS = NUM_SUITS * NUM_CARDS_PER_SUIT;

  var socket = io.connect();
  var deck = new Array();
  var player_id = 0;

  function animateFlip(card) {
    if(card.hasClass("backfacing")){
      card.transition({queue: false, rotateY: "180deg"}, 200);
    } else {
      card.transition({queue: false, rotateY: "0deg"}, 200);
    }
  }

  function flipCard() {
    var card = $(this);

    if(card.hasClass("in_deck")) {
      // Cards in the deck cannot be flipped.
      return;
    }

    card.toggleClass("backfacing");
    if(!card.hasClass("in_own_hand")) {
      socket.emit("flip", card.attr("id"), card.hasClass("backfacing"));
    }
    animateFlip(card);
  }

  function setCardBackfacing(card, backfacing) {
    if(backfacing) {
      card.addClass("backfacing");
    } else {
      card.removeClass("backfacing");
    }
  }

  function createCard(suit, value) {
    var card = $('<div class="card" id="'+suit+'-'+value+'"><div class="frontface"></div><div class="backface"></div></div>')

    card.find(".frontface").css("background-position", (-(value-1) * 83.769) + "px " + (-suit * 121.6) + "px");

    card.on("drag", function(event, ui) {
      var card = $(this);
      var position = $(this).position();
      //console.log("drag " + card.attr("id") + " " + position.left + " " + position.top);
      socket.emit("move", card.attr("id"), position.left, position.top);
    });

    card.on("dragstart", function(event, ui) {
      var card = $(this);
      console.log("dragstart " + card.attr("id"));
      if(card.hasClass("in_deck")) {
        removeTopCardFromDeck();
        socket.emit("pop");
      }
      socket.emit("start_drag", card.attr("id"));
    });

    card.on("dragstop", function(event, ui) {
      var card = $(this);
      console.log("dragend " + card.attr("id"));
      socket.emit("end_drag", card.attr("id"));
    });

    card.on("dblclick", flipCard);

    return card;
  }

  function createCards() {
    for(var i = 0; i < 4; i++) {
      for(var j = 1; j < 14; j++) {
        var card = createCard(i, j);
        $("#table").append(card);
      }
    }
  }

  function addPlayer() {
    var field = $('<div class="player_field"></div>');
    field.droppable({
      drop: function(event, ui) {
        var card = ui.draggable;
        if(!card.hasClass("in_own_hand")) {
          var id = card.attr("id");
          console.log("to_hand", id);
          card.addClass("in_own_hand");
          socket.emit("to_hand", id);
        }
      }
    });
    $("body").append(field);
  }

  function removeTopCardFromDeck() {
    var topCard = _.last(deck)
    topCard.removeClass("in_deck");
    deck = _.initial(deck);
    makeCardDraggable(_.last(deck));
    return topCard;
  }

  function makeCardDraggable(card) {
    console.log("draggable " + card.attr("id"));
    card.draggable({stack: ".card"});
    card.css("pointer-events", "auto");
  }

  socket.on("set_state", function(state) {
    console.log("set_state");
    console.log(state);
    deck = new Array();
    var i = 0;
    _.forEach(state.deck, function(cardID) {
      var card = $("#" + cardID);
      card.addClass("in_deck");
      card.css("z-index", i);
      card.css("pointer-events", "none");
      deck.push(card);
      i += 1;
    });

    makeCardDraggable(_.last(deck));

    _.forEach(state.table, function(cardID) {
      var card = $("#" + cardID);
      makeCardDraggable(card);
    });

    _.forEach(state.hand, function(cardID) {
      var card = $("#" + cardID);
      card.addClass("in_other_hand");
    });

    _.forEach(state.cards, function(cardState) {
      var card = $("#" + cardState.id);
      card.css("left", cardState.x);
      card.css("top", cardState.y);
      setCardBackfacing(card, cardState.backfacing);

      // No animation should be done here.
      if(cardState.backfacing) {
        card.css("transform", "rotateY(180deg)");
      } else {
        card.css("transform", "rotateY(0deg)");
      }
    });
  })

  socket.on("request_cards", function(cards) {
    console.log("Cards received");
    console.log(cards[0]);
    console.log(cards[1]);
    var card_list = new Array();
    card_list.push(createCard(cards[0][0], cards[0][1]));
    //card_list.push(createCard(cards[1][0], cards[1][1]));
    $("body").append(card_list);
  });

  socket.on("registration", function(id_number) {
    console.log(id_number);
    player_id = id_number;
    console.log(player_id);
    socket.emit("request_cards", player_id, 2);
  });

  socket.on("pop", function() {
    console.log("pop");
    var card = removeTopCardFromDeck();
    console.log(card.attr("id"));
  });

  socket.on("start_drag", function(cardID) {
    console.log("disable " + cardID);
    $("#" + cardID).draggable("disable");
  });

  socket.on("end_drag", function(cardID) {
    console.log("enable " + cardID);
    $("#" + cardID).draggable("enable");
  });

  socket.on("to_hand", function(cardID) {
    console.log("to_hand", cardID);
    var card = $("#" + cardID);
    card.addClass("in_other_hand");
    card.css("pointer-events", "none");
    setCardBackfacing(card, true);
    animateFlip(card);
  });

  socket.on("from_hand", function(cardID, backfacing) {
    console.log("to_hand", cardID);
    var card = $("#" + cardID);
    card.removeClass("in_other_hand");
    card.css("pointer-events", "auto");
    setCardBackfacing(card, backfacing);
    animateFlip(card);
  });

  socket.on("move", function(cardID, x, y) {
    //console.log("move " + cardID + " " + x + " " + y);
    $("#" + cardID).css("left", x);
    $("#" + cardID).css("top", y);
  });

  socket.on("flip", function(cardID, backfacing) {
    console.log("flip", cardID, backfacing);
    var card = $("#" + cardID);
    if(backfacing) {
      card.addClass("backfacing");
    } else {
      card.removeClass("backfacing");
    }
    animateFlip(card);
  });

  socket.on("reset_game", function() {
    // todo: remove cards from table and players
    console.log("removing");
  });
  socket.on("shuffle_deck", function(player_id_who_shuffled) {
    // todo: inform that the deck has been shuffled and by who
    console.log("deck shuffled by:");
    console.log(player_id_who_shuffled);
  });

  window.onbeforeunload = function(e) {
    socket.disconnect();
  }

  $("#table").droppable({
    drop: function(event, ui) {
      var card = ui.draggable;
      if(card.hasClass("in_own_hand")) {
        var id = card.attr("id");
        console.log("from_hand", id);
        card.removeClass("in_own_hand");
        socket.emit("from_hand", id, card.hasClass("backfacing"));
      }
    }
  });

  $("#reset").on("click", function() {
    socket.emit("reset_game");
  });

  createCards();
  addPlayer();

  socket.emit("get_state");
});
