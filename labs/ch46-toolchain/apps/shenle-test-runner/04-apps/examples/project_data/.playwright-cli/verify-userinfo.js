async page => {
  const result = await page.evaluate(() => {
    const imgs = Array.from(document.querySelectorAll('img')).map(i => ({
      src: i.src,
      alt: i.alt,
      complete: i.complete,
      naturalWidth: i.naturalWidth,
      naturalHeight: i.naturalHeight,
      visible: i.offsetParent !== null
    }));
    const balanceEl = document.body.innerText.match(/账户余额[\s\S]{0,30}/);
    const sidebarItems = Array.from(document.querySelectorAll('.left a, .sidebar a, .menu a, .user-menu a, ul li a')).map(a => a.textContent.trim()).filter(t => t);
    return {
      imgs: imgs,
      balanceText: balanceEl ? balanceEl[0] : null,
      title: document.title,
      url: location.href
    };
  });
  return JSON.stringify(result, null, 2);
}