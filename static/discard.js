$(function() {
    function createCard(suit, value) {
        var card = $(document.createElement("div")).addClass("card")
                                                   .draggable();

        card.css("background-position", (-(value-1) * 167.538) + "px " + (-suit * 243.2) + "px");

        card.on("drag", function(ev, ui) {
            socket.emit("move", [ui.position.top, ui.position.left]);
        });

        return card;
    }

    var socket = io.connect();

    $("body").append(createCard(0, 7));

    socket.on("move", function(position) {
        var top = position[0];
        var left = position[1];
        $(".card").css("-webkit-transform", "translate("+left+"px,"+top+"px)");
    });
});
