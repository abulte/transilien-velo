function switchInputs () {
  const d = document.getElementById("departure")
  const a = document.getElementById("arrival")
  const old = d.value
  d.value = a.value
  a.value = old
}

window.addEventListener('load', () => {
  var now = new Date();
  now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
  now.setSeconds(0);
  now.setMilliseconds(0);
  var isoString = now.toISOString();
  var datetimeString = isoString.slice(0, -1);
  document.getElementById("datetime").value = datetimeString;
 });
