# validators/image_count.py
from graphql import ValidationRule, GraphQLError


class ImageCountValidator(ValidationRule):
    def enter_field(self, node, *args) -> None:
        if node.name.value == "num_images":
            try:
                value = int(node.value.value)
                if value < 1 or value > 4:
                    self.report_error(
                        GraphQLError("Number of images must be between 1 and 4")
                    )
            except (AttributeError, ValueError):
                self.report_error(GraphQLError("Invalid value for number of images"))
