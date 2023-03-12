import { Component, Inject, ViewEncapsulation } from "@angular/core";
import { TextWidgetProps } from "../../../../bindings/widget/text/TextWidgetProps";
import { WIDGET_PROPS } from "..";

@Component({
    selector: "text-widget",
    templateUrl: "./text-widget.component.html",
    encapsulation: ViewEncapsulation.None,
})
export class TextWidgetComponent {
    public constructor(@Inject(WIDGET_PROPS) public props: TextWidgetProps) {}
}
