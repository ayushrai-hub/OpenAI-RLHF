// ideal_completion.js
function getMFMFirmware(siteNumber) {
    let MFMFirmware = 'A29D.4865';
    if ([1631, 1632, 1701, 1702].includes(siteNumber)) {
        MFMFirmware = 'df21.4865';
    }
    return MFMFirmware;
}
