async page => {
  const result = await page.evaluate(() => {
    const avatars = document.querySelectorAll('img');
    const avatarInfo = [];
    avatars.forEach(img => {
      avatarInfo.push({
        src: img.src,
        alt: img.alt,
        complete: img.complete,
        naturalWidth: img.naturalWidth,
        naturalHeight: img.naturalHeight,
        offsetWidth: img.offsetWidth,
        offsetHeight: img.offsetHeight,
        visible: img.offsetParent !== null
      });
    });
    const nickname = document.querySelector('.userinfo .name, .user-name, .nickname, .username');
    const nicknameText = document.body.innerText.match(/账户余额[\s\S]{0,30}/);
    return {
      avatarInfo: avatarInfo,
      pageTitle: document.title,
      pageURL: location.href,
      nicknameText: nicknameText ? nicknameText[0] : null
    };
  });
  return JSON.stringify(result, null, 2);
}