import nested_admin

from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils.html import format_html, strip_tags

from sis.models import Module, Answer, Attachment, Assignment, Question


class AttachmentInline(nested_admin.NestedGenericStackedInline):
    model = Attachment
    extra = 0


class QuestionInline(nested_admin.NestedStackedInline):
    model = Question
    inlines = [AttachmentInline]
    extra = 0


class AssignmentAdmin(nested_admin.NestedModelAdmin):
    list_display = ('id', 'module_link')
    inlines = [QuestionInline]

    def module_link(self, obj):
        return format_html(
            "<a href={}>{}</a>",
            reverse(
                "admin:sis_module_change",
                args=(obj.module.pk, ),
            ),
            obj.module
        )


class ModuleAdmin(admin.ModelAdmin):
    list_display = ('title', 'created_date', 'updated_date')
    inlines = [AttachmentInline]
    prepopulated_fields = {"slug": ("title",)}


class AnswerAdmin(nested_admin.NestedModelAdmin):
    list_display = ('id', 'author_link', 'question_link')
    inlines = [AttachmentInline]

    def has_add_permission(self, request):
        return False

    def author_link(self, obj):
        return format_html(
            "<a href={}>{}</a>",
            reverse(
                "admin:account_student_changelist",
            )+"?q={}".format(str(obj.author).replace(" ", "+")),
            str(obj.author).title()
        )

    def question_link(self, obj):
        return format_html(
            "<a href={}>{}</a>",
            reverse(
                "admin:sis_assignment_change",
                args=(obj.question.assignment.pk, )),
            strip_tags(obj.question.text))


admin.site.register(Module, ModuleAdmin)
admin.site.register(Assignment, AssignmentAdmin)
admin.site.register(Answer, AnswerAdmin)
