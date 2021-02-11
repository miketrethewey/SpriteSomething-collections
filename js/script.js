// Read a text file
function readTextFile(file) {
  // Create a request
  let rawFile = new XMLHttpRequest();
  let allText = "";
  rawFile.onreadystatechange = function () {
    // If we're ready to read
    if (rawFile.readyState === 4) {
      // If it's OK
      if (rawFile.status === 200 || rawFile.status == 0) {
        // Return the thing
        allText = rawFile.responseText;
        // If it's not OK
      } else if (rawFile.status === 404) {
        // Return null
        return null;
      }
    }
  }

  // Get the thing
  rawFile.open("GET", file, false);
  rawFile.send(null);

  return allText;
}

function listSprites(console, game, path = "./") {
  let sprites_ul = $("<ul>");
  let sprite_li = $("<li>");
  let sprite_a = $("<a>");

  // Sprites
  let manifest = readTextFile(path + console + "\\" + game + "\\manifests\\manifest.json");
  manifest = JSON.parse(manifest);
  for (let key in manifest) {
    let value = manifest[key];
    if (key != "$schema") {
      if ("folder name" in value) {
        let name = value["name"];
        let sprite = value["folder name"];
        sprite_li = $("<li>");
        sprite_a = $("<a>")
          .attr({
            "href": path + console + '/' + game + '/' + sprite + '/'
          })
          .text(name);
        sprite_li.append(sprite_a);
        sprites_ul.append(sprite_li);
      }
    }
  }
  return sprites_ul;
}
function listGames(console, path = "./") {
  let games_ul = $("<ul>");
  let consoleGames = readTextFile(path + console + "\\games.txt");
  consoleGames = consoleGames.split("\n");
  // Games
  for (let game in consoleGames) {
    game = consoleGames[game];
    if (game != "") {
      let game_a = $("<a>")
        .attr({
          "href": path + console + '/' + game + '/'
        });
      let game_li = $("<li>").append(game_a);
      let en_lang = readTextFile(path + console + "\\" + game + "\\lang\\en.json");
      en_lang = JSON.parse(en_lang);
      if ("game" in en_lang) {
        if ("name" in en_lang["game"]) {
          game_a.text(en_lang["game"]["name"]);
        }
      }

      game_li.append(listSprites(console, game, path));
      games_ul.append(game_li);
    }
  }
  return games_ul;
}
function listConsoles(path = "./") {
  let consoles_list = $("<ul>")
    .attr({
      "id": "consoles-list"
    });

  // Consoles
  let consoles = readTextFile(path + "meta\\manifests\\consoles.txt");
  consoles = consoles.split("\n");
  for (let console in consoles) {
    console = consoles[console];
    if (console != "") {
      let console_a = $("<a>")
        .attr({
          "href": path + console + '/'
        })
        .text(console.toUpperCase());
      let console_li = $("<li>").append(console_a);
      console_li.append(listGames(console, path));
      consoles_list.append(console_li);
    }
  }

  return consoles_list;
}

function indexPage() {
  path = "./";
  // SpriteSomething
  let title_a = $("<a>")
    .attr({
      "href": "https://artheau.github.io/SpriteSomething/"
    })
    .text("SpriteSomething");
  let title = $("<h1>")
    .append(title_a);
  $("body").append(title);

  // Custom Sprite Repositories
  let list_ul = $("<ul>");
  let list_li_a = $("<a>")
    .attr({
      "href": path
    })
    .text("Custom Sprite Repositories");
  let list_li = $("<li>")
    .append(list_li_a);
  list_li.append(listConsoles(path));
  list_ul.append(list_li);
  $("body").append(list_ul);
}

function listingPage(console = "", game = "", sprite = "", path = "./") {
  let filepath = window.location.pathname;
  filepath = path;
  let consolepath = console != "" ? filepath + console + '/' : "";
  let gamepath = game != "" ? consolepath + game + '/' : "";
  let spritepath = sprite != "" ? gamepath + sprite + '/' : "";

  // SpriteSomething
  let spritesomething_a = $("<a>")
    .attr({
      "href": path
    })
    .text("SpriteSomething-collections");
  let spritesomething_title = $("<h1>")
    .append(spritesomething_a);
  $("body").append(spritesomething_title);

  if(console != "") {
    // Console
    let console_a = $("<a>")
      .attr({
        "href": consolepath
      })
      .text(console.substring(0, 1).toUpperCase() + console.substring(1))
      .text(console.toUpperCase());
    let console_title = $("<h2>")
      .attr({
        "id": "console-title"
      })
      .append(console_a);
    $("body").append(console_title);

    if(game != "") {
      // Game
      let game_a = $("<a>")
        .attr({
          "href": gamepath
        })
        .text(game.substring(0, 1).toUpperCase() + game.substring(1));

      let en_lang = readTextFile(gamepath + "\\lang\\en.json");
      en_lang = JSON.parse(en_lang);
      if ("game" in en_lang) {
        if ("name" in en_lang["game"]) {
          game_a.text(en_lang["game"]["name"]);
        }
      }

      let gameTitle = $("<h3>")
        .attr({
          "id": "game-title"
        })
        .append(game_a);
      $("body").append(gameTitle);

      if(sprite != "") {
        // Sprite
        let title_a = $("<a>")
          .attr({
            "href": spritepath
          })
          .text(sprite.substring(0, 1).toUpperCase() + sprite.substring(1) + " Sprites");
        let title = $("<h4>")
          .attr({
            "id": "title"
          });
        title.append(title_a);
        $("body").append(title);

        // CSS
        let link = $("<link>")
          .attr({
            "rel": "stylesheet",
            "type": "text/css",
            "href": spritepath + "css.css"
          });
        if (readTextFile(spritepath + "css.css")) {
          $("head").append(link);
        }

        let filename = spritepath + "sprites.json";
        let spritesManifest = readTextFile(filename); // get sprites manifest
        let sprites = null;
        if (spritesManifest) {
          sprites = JSON.parse(spritesManifest); // parse JSON
          sprites.sort(function (a, b) { // sort by name
            return a.file.localeCompare(b.file);
          });
        }

        filename = spritepath + "layer-files.json";
        let layerfilesManifest = readTextFile(filename);
        let layerfiles_container = undefined;
        if (layerfilesManifest) {
          let layerfiles = JSON.parse(layerfilesManifest);
          layerfiles_container = $("<ul>");
          for (let layerext in layerfiles) {
            let layerfile = layerfiles[layerext];
            let app = layerfile["app"];
            let file = layerfile["file"];
            let site = layerfile["site"];
            let repo = layerfile["repo"];
            metas = new Array(
              //layerext,
              file,
              site,
              repo
            );

            let layerfile_li = $("<li>")
              .text(app);
            layerfile_meta_ul = $("<ul>");

            for (let meta in metas) {
              let meta_text = metas[meta];
              if (meta_text) {
                layerfile_meta_li = $("<li>");
                let link_text = "";
                switch (meta) {
                  case "0":
                    link_text = layerext == "png" ? "PNG" : "Layer File";
                    break;
                  case "1":
                    link_text = "Website";
                    break;
                  case "2":
                    link_text = "Source Code";
                    break;
                }
                if (meta_text.indexOf("alttpr") > -1) {
                  switch (meta) {
                    case "0":
                      link_text = "Machine-readable Endpoint";
                      break;
                    case "1":
                      link_text = "Sprite Previews";
                      break;
                  }
                }
                let layerfile_meta_a = $("<a>")
                  .attr({
                    "href": meta_text
                  })
                  .text(link_text);
                layerfile_meta_li.append(layerfile_meta_a);
                layerfile_meta_ul.append(layerfile_meta_li);

                if (link_text == "Sprite Previews") {
                  link_text = "Downloadable Sprite Previews";
                  meta_text = "http://alttp.mymm1.com/sprites";
                  layerfile_meta_li = $("<li>");
                  layerfile_meta_a = $("<a>")
                    .attr({
                      "href": meta_text
                    })
                    .text(link_text);
                  layerfile_meta_li.append(layerfile_meta_a);
                  layerfile_meta_ul.append(layerfile_meta_li);
                }
              }
            }
            layerfile_li.append(layerfile_meta_ul);
            layerfiles_container.append(layerfile_li);
          }
        }

        let sprites_container = $("<div>")
          .attr({
            "id": "sprites-container"
          });

        for (let sprite in sprites) { // iterate through sprites
          sprite = sprites[sprite]; // get this sprite
          let name = sprite.name; // sprite name
          let author = sprite.author; // sprite author
          let file = sprite.file; // sprite url
          let img = file;
          if (sprite.hasOwnProperty("preview")) {
            img = sprite.preview;
          }
          if (img.endsWith(".zspr")) {
            img = img.substring(img.lastIndexOf('/') + 1);
            img = img.substring(0, img.length - 5);
            img = "./sheets/thumbs/" + img + ".png";
          }
          let name_link = $("<a>")
            .attr({
              "href": file
            })
            .text(name); // name link
          let name_line = $("<div>")
            .attr({
              "class": "name"
            })
            .append(name_link); // name container
          let author_line = $("<div>")
            .attr({
              "class": "author"
            })
            .text(author); // author container
          let sprite_image = $("<div>")
            .attr({
              "class": "sprite-preview",
              "style": "background-image:url(" + img + ")"
            }); // image container
          let sprite_object = $("<div>")
            .attr({
              "class": "sprite"
            })
            .append(name_line)
            .append(author_line)
            .append(sprite_image); // main container
          sprites_container.append(sprite_object);
        }

        $("body").append(sprites_container);
        let spacer = $("<div>")
          .attr({
            "style": "clear:both"
          });
        $("body").append(spacer);
        if (typeof layerfiles_container !== "undefined") {
          $("body").append(layerfiles_container);
        }
      } else {
        let sprites_ul = listSprites(console, game, path);
        $("body").append(sprites_ul);
      }
    } else {
      let games_ul = listGames(console, path);
      $("body").append(games_ul);
    }
  }
}

function forkMe() {
  let title = "Contribute yours!";
  let stylesheet = $("<link>")
    .attr({
      "rel": "stylesheet",
      "href": "https://cdnjs.cloudflare.com/ajax/libs/github-fork-ribbon-css/0.2.3/gh-fork-ribbon.min.css",
      "type": "text/css"
    });
  let a = $("<a>")
    .attr({
      "class": "github-fork-ribbon right-top",
      "href": "https://github.com/miketrethewey/SpriteSomething-collections/blob/gh-pages/CONTRIBUTING.md",
      "data-ribbon": title,
      "title": title
    })
    .text(title);
  $("head").append(stylesheet);
  $("body").append(a);
}

function init(mode = "index") {
  // Sanity check, only process if we've got 3 parts, will care about less parts later for console/game pages
  if (mode.indexOf('/') > -1) {
    modepieces = mode.split('/');
    if (mode.length < 3) {
      mode = "index";
    }
  }
  // Index
  if (mode == "index") {
    forkMe();
    indexPage();
  } else {
    forkMe();

    // Get console/game/sprite
    mode = mode.split('/');
    let console = mode.length > 0 ? mode[0] : "";
    let game = mode.length > 1 ? mode[1] : "";
    let sprite = mode.length > 2 ? mode[2] : "";

    listingPage(console, game, sprite);
  }
}
