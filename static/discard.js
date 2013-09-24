$(function() {
  var NUM_SUITS = 4
  var NUM_CARDS_PER_SUIT = 13
  var NUM_CARDS = NUM_SUITS * NUM_CARDS_PER_SUIT;

  var socket = io.connect();
  var deck = new Array();
  var player_id = 0;

  function animateFlip(card) {
    if($(card).hasClass("backfacing")){
      $(card).transition({queue: false, rotateY: "180deg"});
    } else {
      $(card).transition({queue: false, rotateY: "0deg"});
    }
  }

  function flipCard() {
    if($(this).hasClass("in_deck")) {
      // Cards in the deck cannot be flipped.
      return;
    }

    $(this).toggleClass("backfacing");
    socket.emit("backfacing", $(this).hasClass("backfacing"));
    animateFlip(this);
  }


  function createCard(suit, value) {
    var card = $('<div class="card" id="'+suit+'-'+value+'"><div class="frontface"></div><div class="backface"></div></div>')

    card.find(".frontface").css("background-position", (-(value-1) * 167.538) + "px " + (-suit * 243.2) + "px");

    card.on("drag", function(event, ui) {
      var card = $(this);
      console.log("drag " + card.attr("id"));
      var position = $(this).position();
      socket.emit("move", card.attr("id"), position.left, position.top);
    });

    card.on("dragstart", function(event, ui) {
      var card = $(this);
      console.log("dragstart " + card.attr("id"));
      if(card.hasClass("in_deck")) {
        removeTopCardFromDeck();
        socket.emit("pop_card");
      }
      socket.emit("start_drag", card.attr("id"));
    });

    card.on("dblclick", flipCard);

    return card;
  }

  function createCards() {
    for(var i = 0; i < 4; i++) {
      for(var j = 1; j < 14; j++) {
        var card = createCard(i, j);
        $("body").append(card);
      }
    }
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

    _.forEach(state.cards, function(cardState) {
      var card = $("#" + cardState.id);
      card.css("left", cardState.x);
      card.css("top", cardState.y);
      if(cardState.backfacing) {
        card.addClass("backfacing");
        card.css("-webkit-transition", "rotateY(180deg)");
      } else {
        card.removeClass("backfacing");
        card.css("-webkit-transition", "rotateY(0deg)");
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

  socket.on("pop_card", function() {
    console.log("pop_card");
    var card = removeTopCardFromDeck();
    console.log(card.attr("id"));
    card.draggable("disable");
  });

  socket.on("start_drag", function(cardID) {
    console.log("disable " + cardID);
    $("#" + cardID).draggable("disable");
  });

  socket.on("end_drag", function(cardID) {
    $(".card").transition({queue: false, x: position[1], y: position[0]});
  });

  socket.on("move", function(cardID, position) {
    $("#" + cardID).transition({queue: false, x: position[1], y: position[0]});
  });

  socket.on("backfacing", function(backfacing) {
    console.log("Backfacing", backfacing);
    $(".card").toggleClass("backfacing", backfacing);
    animateFlip($(".card"));
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

  createCards();

  socket.emit("get_state");
});
