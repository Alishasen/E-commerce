from django.db import models
class Category(models.Model):

    name = models.CharField(
        max_length=100,
        unique=True
    )

    def __str__(self):
        return self.name

class Product(models.Model):

    name = models.CharField(max_length=200)

    description = models.TextField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    stock = models.PositiveIntegerField(
        default=0
    )

    discount = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0
    )

    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products"
    )

    is_trending = models.BooleanField(
        default=False
    )

    # Products are never hard-deleted once they've been ordered
    # (OrderItem.product is PROTECT, on purpose, so past orders keep
    # their real product data intact). "Deleting" a product from the
    # admin side instead deactivates it: it disappears from the
    # storefront but stays intact for order history.
    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    def __str__(self):
        return self.name

class ProductImage(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
    )

    image = models.ImageField(
        upload_to="products/"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.product.name} image"


class Banner(models.Model):

    image = models.ImageField(
        upload_to="banners/"
    )

    title = models.CharField(
        max_length=200,
        blank=True
    )

    description = models.CharField(
        max_length=300,
        blank=True
    )

    button_text = models.CharField(
        max_length=50,
        default="Shop Now"
    )

    button_url = models.CharField(
        max_length=200,
        default="/products/"
    )

    is_active = models.BooleanField(
        default=True
    )

    order = models.PositiveIntegerField(
        default=0
    )

    def __str__(self):
        return self.title or f"Banner {self.order}"
    
    
class Order(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
        ("completed", "Completed"),
    ]

    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="orders",
    )

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )

    # ------------------------------------------------------------
    # Contact info, snapshotted at the time of the order so later
    # changes to the user's profile never alter past orders.
    # ------------------------------------------------------------

    full_name = models.CharField(
        max_length=150,
        blank=True,
        default="",
    )

    email = models.EmailField(
        blank=True,
        default="",
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        default="",
    )

    # ------------------------------------------------------------
    # Shipping address, also snapshotted per order.
    # ------------------------------------------------------------

    shipping_address = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    shipping_city = models.CharField(
        max_length=100,
        blank=True,
        default="",
    )

    shipping_notes = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"Order #{self.pk}"
    
class OrderItem(models.Model):

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT,
    )

    quantity = models.PositiveIntegerField()

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    subtotal = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    def __str__(self):
        return (
            f"{self.product.name} "
            f"x {self.quantity}"
        )
        
class Payment(models.Model):

    PAYMENT_METHOD_CHOICES = [

        ("esewa", "eSewa"),
        ("cod", "Cash on Delivery"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("success", "Success"),
        ("failed", "Failed"),
    ]

    order = models.OneToOneField(
        Order,
        on_delete=models.CASCADE,
        related_name="payment",
    )

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
    )

    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )

    # KHOJ's own internal reference for this payment attempt
    # (e.g. "KHOJ-<order id>-<timestamp>"). For eSewa this is sent
    # out as transaction_uuid; for COD it can just identify the order.
    transaction_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    # eSewa's own reference id (ref_id) returned once THEY confirm
    # the payment. Kept separate from transaction_id above because
    # that one is ours, not eSewa's.
    esewa_ref_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
    )

    status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="pending",
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"Payment for Order #{self.order.id}"
class Review(models.Model):

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="reviews",
    )

    user = models.ForeignKey(
        "auth.User",
        on_delete=models.CASCADE,
        related_name="product_reviews",
    )

    rating = models.PositiveIntegerField(
        choices=[
            (1, "1 Star"),
            (2, "2 Stars"),
            (3, "3 Stars"),
            (4, "4 Stars"),
            (5, "5 Stars"),
        ]
    )

    comment = models.TextField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["product", "user"],
                name="unique_product_review_per_user",
            )
        ]

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating}/5)"