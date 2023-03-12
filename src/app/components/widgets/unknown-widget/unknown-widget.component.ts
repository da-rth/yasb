import { Component, Inject, ViewEncapsulation } from "@angular/core";
import { WIDGET_PROPS } from "..";
import { UnknownWidgetProps } from "../../../../bindings/widget/unknown/UnknownWidgetProps";

@Component({
    selector: "unknown-widget",
    templateUrl: "./unknown-widget.component.html",
    encapsulation: ViewEncapsulation.None,
})
export class UnknownWidgetComponent {
    public constructor(@Inject(WIDGET_PROPS) public props: UnknownWidgetProps) {}

    public get widgetLabel(): string {
        return `${this.props.kind} is not a valid widget.`;
    }
}
