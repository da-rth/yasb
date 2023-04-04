import humanizeDuration from "humanize-duration";
import prettyBytes from "pretty-bytes";
import { Options } from "pretty-bytes";

/**
 * Short-hand helper function for displaying fractions as percentage strings
 * @param partial The numerator of the percentage fraction.
 * @param total The demoninator of the percentage fraction. Defaults to 100.
 * @returns The resulting fraction formatted as a percentage string e.g. "30%".
 */
export function percent(partial: number, total = 100) {
    return `${Math.round((partial / total) * 100)}%`;
}

/**
 * Short-hand formatting function for building a Font Awesome HTML icon
 * See: https://fontawesome.com/icons
 * and: https://www.npmjs.com/package/@fortawesome/fontawesome-free
 * @param icon The Font Awesome Icon to be displayed e.g. 'magnifying-glass'.
 * @param iconType The type of Material Icon e.g. solid, regular, brands.
 * @param cls Additional classes to be applied to the icon.
 * @returns HTML Element string e.g. <i class="faIcon fa fa-magnifying-glass my-class"></i>".
 */
export function faIcon(icon: string, iconType?: string, cls?: string): string {
    return `<i class='faIcon ${iconType ?? "fa"} fa-${icon} ${cls ?? ""}'></i>`;
}

/**
 * Short-hand formatting function for building a material HTML icon
 * See: https://developers.google.com/fonts/docs/material_icons
 * and: https://www.npmjs.com/package/material-icons
 * @param icon The Material Icon to be displayed e.g. 'search'.
 * @param iconType The type of Material Icon e.g. outlined, round, sharp, two-tone or undefined.
 * @param cls Additional classes to be applied to the icon.
 * @returns HTML Element string e.g. <i class="matIcon material-icons-outlined my-class">search</i>".
 */
export function matIcon(icon: string, iconType?: string, cls?: string): string {
    const matCls = iconType ? `material-icons-${iconType}` : "material-icons";
    return `<i class="matIcon ${matCls} ${cls ?? ""}">${icon}</i>`;
}

/**
 * Short-hand formatting function for pretty-formatting numerical byte values.
 * See: https://www.npmjs.com/package/pretty-bytes
 * and: https://github.com/sindresorhus/pretty-bytes#prettybytesnumber-options
 * @param value The amount of bytes to be prettified e.g. 256000 (bytes).
 * @param options PrettyBytes Options.
 * @returns string - Prettified bytes e.g. 256 kB.
 */
export function pBytes(value: number, options?: Options): string {
    return prettyBytes(value, options);
}

/**
 * Short-hand formatting function for humanizing a provided millisecond duration value
 * See: https://www.npmjs.com/package/humanize-duration
 * @param ms The number of milliseconds to be humanized e.g. 1000
 * @param options An object containing options for how the value should be humanized.
 * @returns The humanized duration as a string e.g. "1 second"
 */
export function humanize(ms: number, options?: humanizeDuration.Options) {
    return humanizeDuration(ms, options);
}
