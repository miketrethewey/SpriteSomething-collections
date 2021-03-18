// Index Elements
function index_elements(selector,payload) {
  let list = payload;
  for(let console of list.split("\n")) {
    if(console.trim() != "") {
      console = console.trim();
      $(selector).append($("<li>")
        .append($("<a>")
          .attr({
            "class": console,
            "href": path_join([data["project"]["url"],console])
          })
          .text(console.toUpperCase())
        )
      )
    }
  }
}

// Console Elements
function console_elements(selector,payload) {
  if(selector.indexOf("title") > -1) {
    // If it's the Game Title
    // Set Game Name
    console.log(payload);

  } else if(selector.indexOf("gamelist") > -1) {
    // If it's the Console Game List
    let list = payload;
    for(let game of list.split("\n")) {
      // List the Games
      if(game.trim() != "") {
        game = game.trim();
        $(selector).append($("<li>")
          .append($("<a>")
            .attr({
              "class": game,
              "href": path_join([data["console"]["url"],game])
            })
            .text(game)
          )
        );
        fetch(path_join([data["console"]["url"],game.trim(),"lang","en.json"]))
          .then(status)
          .then(parse)
          .then(function(payload) {
            text = payload["game"]["name"];
            $("a." + game).text(text);
          });
      }
    }
  }
}

// Game Elements
function game_elements(selector,payload) {
  if(selector.indexOf("title") > -1) {
    // If it's the Game Title
    // Set Game Name
    text = payload["game"]["name"];
    $("title").text($("title").text() + '/' + text);
    $(selector).text(text);
    data["game"]["name"] = text;

  } else if(selector.indexOf("spritelist") > -1) {
    // If it's the Game Sprite List
    // List the Sprites
    let manifest = payload;
    for(let spriteID in manifest) {
      if(spriteID != "$schema") {
        let sprite = manifest[spriteID];
        spritefolder = sprite["folder name"].trim();
        $(selector)
          .append($("<li>")
            .append(
              $("<a>").attr({
                "href": path_join([data["game"]["url"],spritefolder])
              })
              .text(sprite["name"])
            )
          )
      }
    }
  }
}

// Sprite Elements
function sprite_elements(selector,payload) {
  if(selector.indexOf("title") > -1) {
    // Set Sprite Name
    text = payload[1]["name"];
    $("title").text($("title").text() + path_sep() + text);
    text += " Sprites";
    $(selector).text(text);
  } else if(selector.indexOf("previewlist") > -1) {
    // Sprite Listing
    sprites = payload;
    sprites.sort(function(a,b) {
      x = a.file.toLowerCase();
      y = b.file.toLowerCase();
      return x < y ? -1 : x > y ? 1 : 0;
    });
    for(sprite of sprites) {
      filext = sprite["file"].substring(sprite["file"].lastIndexOf('.') + 1);
      filexts = ["png","gif"];
      if((!("preview" in sprite)) && (!filexts.includes(filext))) {
        sprite["preview"] = path_join([data["sprite"]["url"],"sheets","thumbs",sprite["slug"] + '.' + sprite["version"] + ".png"]);
      }
      add_template(
        "spritePreview",
        sprite
      )
    }
  } else if(selector.indexOf("resources") > -1) {
    // Resource Listing
    resources = payload;
    for(resource in resources) {
      if(resource != "vt") {
        resource = resources[resource];
        add_template(
          "resource",
          resource
        )
      }
    }
  }
}
