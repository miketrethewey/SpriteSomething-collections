// Fetch a URL and do stuff
function fetch_and_insert(url,selector) {
  // Fetch the URL
  fetch(url)
    // Get HTTP status
    .then(status)
    // Parse data
    .then(parse)
    // Do stuff
    .then(function(payload) {
      let text = "";
      if(selector.indexOf("index") > -1) {
        index_elements(selector,payload);
      } else if(selector.indexOf("console") > -1) {
        console_elements(selector,payload);
      } else if(selector.indexOf("game") > -1) {
        game_elements(selector,payload);
      } else if(selector.indexOf("sprite") > -1) {
        sprite_elements(selector,payload);
      }
      if(text != "") {
        $(selector).text(text);
      }
    })
    .catch(function(error) {
      console.log("Request failed:", error, "\n" + "URL:", url, "\n" + "Selector:", selector);
    });
}

// Get a template, copy it, manip it
function add_template(name,attrs) {
  if(name.indexOf("Header") > -1) {
    // If it's a Header
    tmp = $("#" + name)[0].content.cloneNode(true);
    $(tmp).find("a")
      .attr({
        "href": attrs["href"]
      })
      .text(attrs["text"]);
      $("body").append(tmp);
  } else if(name == "spritePreview") {
    // If it's a Sprite Preview
    tmp = $("#spritePreview")[0].content.cloneNode(true);
    if(!("preview" in attrs)) {
      attrs["preview"] = attrs["file"];
    }
    $(tmp).find(".name a")
      .attr({
        "href": attrs["file"]
      })
      .text(attrs["name"]);
    $(tmp).find(".author").text(attrs["author"]);
    $(tmp).find(".sprite-preview")
      .attr({
        "style": "background-image:url(" + attrs["preview"] + ")"
      });
    if("usage" in attrs) {
      console.log(attrs["usage"]);
      if(attrs["usage"].indexOf("global") > -1) {
        attrs["usage"] = attrs["usage"].indexOf("commercial") > -1 ? ["commercial","global"] : ["global"];
      }
      if(attrs["usage"].indexOf("commercial") < 0) {
        attrs["usage"].push("commercial-no")
      }
      attrs["usage"].sort();
      for(let usage of attrs["usage"]) {
        let no = usage.endsWith("-no");
        if(no) {
          usage = usage.substr(0,usage.length - 3);
        }
        let title = usage.substr(0,1).toUpperCase() + usage.substr(1);
        if(["smz3","varia"].indexOf(usage) > -1) {
          title = title.toUpperCase();
        }
        if(no) {
          title = "NO " + title;
        }
        let iconDiv = $("<div>")
          .attr("class","usage-icon " + "u-" + usage)
          .attr("title", title);
        if(no) {
          iconDiv.append($("<img>")
            .attr("src","../../../icons/usage/no.png")
          )
        }
        $(tmp).find(".sprite").append(iconDiv);
      }
    }
    $("#sprite-previewlist").append(tmp);
  } else if(name == "resource") {
    // If it's a Resource link
    tmp = $("#resourceList")[0].content.cloneNode(true);
    $(tmp).find(".app").text(attrs["app"]);
    for(let link of ["file","site","repo"]) {
      if(link in attrs) {
        $(tmp).find('.' + link + " a")
          .attr({
            "href": attrs[link]
          });
          if(link == "file" && attrs["app"] == "Various") {
            $(tmp).find('.' + link + " a").text(attrs["file"].substr(attrs["file"].lastIndexOf('.') + 1).toUpperCase());
          }
      } else {
        $(tmp).find('.' + link)
          .attr({
            "style": "display:none"
          })
      }
    }
    $("#sprite-resources").append(tmp);
    if(data["game"]["slug"] == "zelda3" && data["sprite"]["slug"] == "link" && attrs["app"].indexOf("GIMP") > -1) {
      // If we're adding Z3R's stuff
      fetch(path_join([data["sprite"]["url"],"linklist.json"]))
        .then(status)
        .then(parse)
        .then(function(payload) {
          let linklist = payload;
          add_linklist({
            "name": "A Link to the Past Randomizer 'Official' Sprites",
            "links": linklist
          });
        });
    }
  }
}

// Add a Link list to #resources
function add_linklist(attrs) {
  let list_li = $("<li>").text(attrs["name"]);
  let ul = $("<ul>");

  for(let link of attrs["links"]) {
    let li = $("<li>");
    let a = $("<a>").attr({"href":link["url"]}).text(link["name"]);
    li.append(a);
    ul.append(li);
  }

  list_li.append(ul);
  $("#sprite-resources").append(list_li);
}
