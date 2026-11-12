from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models
from django.utils.text import slugify



# 1. ONE-TO-ONE RELATIONSHIP
class UserProfile(models.Model):
    """Extends Django's built-in User model with profile-specific metadata."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    bio = models.TextField(blank=True)
    website = models.URLField(blank=True)

    def __str__(self):
        return f"Profile: {self.user.username}"


# SUPPORTING MODELS (Categories & Tags)
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=60, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name



# 2. MANY-TO-ONE RELATIONSHIPS (ForeignKeys)
class Post(models.Model):
    class Status(models.TextChoices):
        DRAFT = "DF", "Draft"
        PUBLISHED = "PB", "Published"

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    body = models.TextField()
    status = models.CharField(
        max_length=2,
        choices=Status,
        default=Status.DRAFT,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Many-to-One: One user writes many posts
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="blog_posts",
    )

    # Many-to-One: One category contains many posts
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="posts",
    )

    # Standard Many-to-Many: A post can have many tags
    tags = models.ManyToManyField(
        Tag,
        blank=True,
        related_name="posts",
    )


    # 3. MANY-TO-MANY WITH CUSTOM THROUGH MODEL
    # Users can bookmark posts, storing extra fields on the intermediate table.
    bookmarked_by = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through="UserBookmark",
        related_name="bookmarked_posts",
        blank=True,
    )

    class Meta:
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class UserBookmark(models.Model):
    """Custom intermediate table for the User <-> Post Many-to-Many relationship."""

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    saved_at = models.DateTimeField(auto_now_add=True)
    notes = models.CharField(max_length=255, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "post"], name="unique_user_post_bookmark"
            )
        ]
        ordering = ["-saved_at"]

    def __str__(self):
        return f"{self.user.username}'s bookmark for '{self.post.title}'"