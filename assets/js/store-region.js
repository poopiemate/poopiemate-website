// App Store 나라 고르기 — 나라 코드가 없는 App Store 링크는 PC 브라우저에서 늘 미국 스토어로 열린다.
// 브라우저 언어의 지역(en-GB → gb)을 먼저 보고, 없거나 미국이면 기기 시간대로 나라를 짐작한다. 끝내 모르면 null(링크 그대로).
(function () {
  var TZ = {
    'Asia/Seoul': 'kr', 'Asia/Tokyo': 'jp', 'Asia/Shanghai': 'cn', 'Asia/Hong_Kong': 'hk', 'Asia/Taipei': 'tw', 'Asia/Singapore': 'sg',
    'Asia/Kolkata': 'in', 'Asia/Calcutta': 'in', 'Asia/Bangkok': 'th', 'Asia/Jakarta': 'id', 'Asia/Manila': 'ph', 'Asia/Ho_Chi_Minh': 'vn',
    'Asia/Saigon': 'vn', 'Asia/Kuala_Lumpur': 'my', 'Asia/Dubai': 'ae', 'Asia/Riyadh': 'sa', 'Asia/Jerusalem': 'il', 'Asia/Karachi': 'pk',
    'Europe/London': 'gb', 'Europe/Dublin': 'ie', 'Europe/Paris': 'fr', 'Europe/Berlin': 'de', 'Europe/Madrid': 'es', 'Europe/Rome': 'it',
    'Europe/Amsterdam': 'nl', 'Europe/Brussels': 'be', 'Europe/Zurich': 'ch', 'Europe/Vienna': 'at', 'Europe/Stockholm': 'se',
    'Europe/Oslo': 'no', 'Europe/Copenhagen': 'dk', 'Europe/Helsinki': 'fi', 'Europe/Warsaw': 'pl', 'Europe/Lisbon': 'pt',
    'Europe/Prague': 'cz', 'Europe/Budapest': 'hu', 'Europe/Athens': 'gr', 'Europe/Istanbul': 'tr', 'Europe/Bucharest': 'ro',
    'Europe/Kiev': 'ua', 'Europe/Kyiv': 'ua', 'Europe/Luxembourg': 'lu',
    'Australia/Sydney': 'au', 'Australia/Melbourne': 'au', 'Australia/Brisbane': 'au', 'Australia/Perth': 'au', 'Australia/Adelaide': 'au',
    'Australia/Hobart': 'au', 'Australia/Darwin': 'au', 'Pacific/Auckland': 'nz',
    'America/Toronto': 'ca', 'America/Vancouver': 'ca', 'America/Edmonton': 'ca', 'America/Winnipeg': 'ca', 'America/Halifax': 'ca',
    'America/Mexico_City': 'mx', 'America/Sao_Paulo': 'br', 'America/Argentina/Buenos_Aires': 'ar', 'America/Bogota': 'co',
    'America/Santiago': 'cl', 'America/Lima': 'pe', 'Africa/Johannesburg': 'za', 'Africa/Lagos': 'ng', 'Africa/Cairo': 'eg', 'Africa/Nairobi': 'ke'
  };
  window.pmAppStoreCountry = function () {
    var langs = navigator.languages && navigator.languages.length ? navigator.languages : [navigator.language || ''];
    var region = null;
    for (var i = 0; i < langs.length; i++) {
      var m = /^[a-z]{2,3}[-_]([a-z]{2})(?:$|[-_])/i.exec(langs[i] || '');
      if (m) { region = m[1].toLowerCase(); break; }
    }
    if (region && region !== 'us') return region;
    var tz = '';
    try { tz = Intl.DateTimeFormat().resolvedOptions().timeZone || ''; } catch (e) {}
    if (TZ[tz]) return TZ[tz];
    return region;
  };
  // 나라 코드가 없는 App Store 링크에 나라를 넣는다
  window.pmAppStoreUrl = function (url) {
    var cc = window.pmAppStoreCountry();
    return cc ? url.replace('https://apps.apple.com/app/', 'https://apps.apple.com/' + cc + '/app/') : url;
  };
})();
