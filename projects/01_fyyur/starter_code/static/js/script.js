window.parseISOString = function parseISOString(s) {
  var b = s.split(/\D+/);
  return new Date(Date.UTC(b[0], --b[1], b[2], b[3], b[4], b[5], b[6]));
};

async function delete_venue(venue) {
  // Delete request cannot be submited through web forms or anchor tags
  await fetch("/venues/" + venue, { method: "delete" });
  window.location.replace("/");
}
