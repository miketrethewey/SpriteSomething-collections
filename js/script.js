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

function init(mode = "index") {
  if (mode.indexOf('/') > -1) {
    modepieces = mode.split('/');
    if (mode.length < 3) {
      mode = "index";
    }
  }
  // Index
  if (mode == "index") {
    // SpriteSomething
    let title = $("<h1></h1>")
      .attr({
        "id": "title"
      })
      .text("SpriteSomething");
    $("body").append(title);

    let list_li = $("<ul><li>")
      .text("Custom Sprite Repositories");
    let consoles_list = $("<ul>")
      .attr("id", "consoles-list");
    list_li.append(consoles_list);
    $("body").append(list_li);

    let consoles = readTextFile(".\\meta\\manifests\\consoles.txt");
    consoles = consoles.split("\n");
    for (let console in consoles) {
      console = consoles[console];
      if (console != "") {
        let console_li = $("<li>").text(console.toUpperCase());
        let consoleGames = readTextFile(".\\" + console + "\\games.txt");
        consoleGames = consoleGames.split("\n");
        for (let game in consoleGames) {
          game = consoleGames[game];
          if (game != "") {
            let games_ul = $("<ul>");
            let game_li = $("<li>");
            let sprites_ul = $("<ul>");
            let sprite_li = $("<li>");
            let sprite_a = $("<a>");
            let en_lang = readTextFile(".\\" + console + "\\" + game + "\\lang\\en.json");
            en_lang = JSON.parse(en_lang);
            if ("game" in en_lang) {
              if ("name" in en_lang["game"]) {
                game_li.text(en_lang["game"]["name"]);
              }
            }

            let manifest = readTextFile(".\\" + console + "\\" + game + "\\manifests\\manifest.json");
            manifest = JSON.parse(manifest);
            for (let key in manifest) {
              let value = manifest[key];
              if (key != "$schema") {
                if ("folder name" in value) {
                  let name = value["name"];
                  let sprite = value["folder name"];
                  sprite_li = $("<li>");
                  sprite_a = $("<a>")
                    .attr("href", "./?mode=" + console + '/' + game + '/' + sprite)
                    .text(name);
                  sprite_li.append(sprite_a);
                  sprites_ul.append(sprite_li);
                }
              }
            }
            game_li.append(sprites_ul);
            games_ul.append(game_li);
            console_li.append(games_ul);
            consoles_list.append(console_li);
          }
        }
      }
    }
  } else {
    mode = mode.split('/');
    let console = mode[0];
    let game = mode[1];
    let sprite = mode[2];

    let filepath = window.location.pathname;
    filepath = filepath.replace("index.html","");
    filepath += console + '/';
    filepath += game + '/';
    filepath += sprite + '/';

    let gameTitle = $("<h1>")
      .text(game.substring(0, 1).toUpperCase() + game.substring(1))
      .attr("id", "gameTitle");
    $("body").append(gameTitle);

    let title_a = $("<a>")
      .attr("href", filepath + "./")
      .text(sprite.substring(0, 1).toUpperCase() + sprite.substring(1) + " Sprites");
    let title = $("<h2>")
      .attr("id", "title");
    title.append(title_a);
    $("body").append(title);

    let link = $("<link>")
      .attr("rel", "stylesheet")
      .attr("type", "text/css")
      .attr("href", filepath + "css.css");
    if (readTextFile(filepath + "css.css")) {
      $("head").append(link);
    }

    let filename = filepath + "sprites.json";
    let spritesManifest = readTextFile(filename); // get sprites manifest
    let sprites = null;
    if (spritesManifest) {
      sprites = JSON.parse(spritesManifest); // parse JSON
      sprites.sort(function (a, b) { // sort by name
        return a.name.localeCompare(b.name);
      });
    }

    filename = filepath + "layer-files.json";
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
              .attr("href", meta_text)
              .text(link_text);
            layerfile_meta_li.append(layerfile_meta_a);
            layerfile_meta_ul.append(layerfile_meta_li);

            if (link_text == "Sprite Previews") {
              link_text = "Downloadable Sprite Previews";
              meta_text = "http://alttp.mymm1.com/sprites";
              layerfile_meta_li = $("<li>");
              layerfile_meta_a = $("<a>")
                .attr("href", meta_text)
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
      .attr("id", "sprites_container");

    for (let sprite in sprites) { // iterate through sprites
      sprite = sprites[sprite]; // get this sprite
      let name = sprite.name; // sprite name
      let author = sprite.author; // sprite author
      let file = sprite.file; // sprite url
      let img = file;
      if (sprite.hasOwnProperty("preview")) {
        img = sprite.preview;
      }
      let name_link = $("<a>")
        .attr("href", file)
        .text(name); // name link
      let name_line = $("<div>")
        .attr("class", "name")
        .append(name_link); // name container
      let author_line = $("<div>")
        .attr("class", "author")
        .text(author); // author container
      let sprite_image = $("<div>")
        .attr("class", "sprite-preview")
        .attr("style", "background-image:url(" + img + ")"); // image container
      let sprite_object = $("<div>")
        .attr("class", "sprite")
        .append(name_line)
        .append(author_line)
        .append(sprite_image); // main container
      sprites_container.append(sprite_object);
    }

    $("body").append(sprites_container);
    let spacer = $("<div>")
      .attr("style", "clear:both");
    $("body").append(spacer);
    if (typeof layerfiles_container !== "undefined") {
      $("body").append(layerfiles_container);
    }
  }
}
