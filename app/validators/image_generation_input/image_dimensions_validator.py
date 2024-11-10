# validators/image_dimensions.py
from graphql import ValidationRule, GraphQLError


class ImageDimensionsValidator(ValidationRule):
    def enter_field(self, node, *args) -> None:
        if node.name.value in ["width", "height"]:
            try:
                value = int(node.value.value)
                if value < 64 or value > 1024:
                    self.report_error(
                        GraphQLError(
                            f"Image {node.name.value} must be between 64 and 1024 pixels"
                        )
                    )
                if value % 64 != 0:
                    self.report_error(
                        GraphQLError(
                            f"Image {node.name.value} must be a multiple of 64"
                        )
                    )
            except (AttributeError, ValueError):
                self.report_error(GraphQLError(f"Invalid value for {node.name.value}"))
