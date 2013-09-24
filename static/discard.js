$(function() {
  var NUM_SUITS = 4
  var NUM_CARDS_PER_SUIT = 13
  var NUM_CARDS = NUM_SUITS * NUM_CARDS_PER_SUIT;

  var socket = io.connect();
  var player_id = 0;

  function animateFlip(card) {
    if($(card).hasClass("backfacing")){
      $(card).transition({queue: false, rotateY: "180deg"});
    } else {
      $(card).transition({queue: false, rotateY: "0deg"});
    }
  }

  function flipCard(card) {
    $(this).toggleClass("backfacing");
    socket.emit("backfacing", $(this).hasClass("backfacing"));
    animateFlip(this);
  }

  function createCard(suit, value) {
    var card = $('<div class="card backfacing" id="'+suit+'-'+value+'"><div class="frontface"></div><div class="backface"></div></div>')

    card.find(".frontface").css("background-position", (-(value-1) * 167.538) + "px " + (-suit * 243.2) + "px");

    card.on("drag", function(ev, ui) {
      socket.emit("move", [ui.position.top, ui.position.left]);
    });

    card.on("dblclick", flipCard);

    return card;
  }

  function createDeck() {
    var cards = new Array();
    for(var i = 0; i < 4; i++) {
      for(var j = 1; j < 14; j++) {
        var card = createCard(i, j);
        card.css("pointer-events", "none");
        cards.push(card);
      }
    }

    cards = _.shuffle(cards);

    for(var i = 0; i < cards.length; i++) {
      var card = cards[i];
      card.css("left", i * 0.5 + "px");
      card.css("top", i * 0.5 + "px");
      card.css("z-index", i);
      $("body").append(card);
    }

    var lastCard = cards[cards.length-1];
    lastCard.draggable({stack: ".card"});
    lastCard.css("pointer-events", "auto");
  }

  createDeck();

  socket.emit("registration");

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

  socket.on("move", function(position) {
    $(".card").transition({queue: false, x: position[1], y: position[0]});
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
});
