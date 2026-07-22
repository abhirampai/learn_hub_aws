# LearnHub Authorization

## Roles

- student
- instructor
- admin

## Course permissions

| Action | Student | Instructor | Admin |
|---|---:|---:|---:|
| Create course | No | Yes | Yes |
| Update own course | No | Yes | Yes |
| Update another instructor's course | No | No | Yes |
| Publish own course | No | Yes | Yes |
| Delete own course | No | Yes | Yes |
| Delete another instructor's course | No | No | Yes |

## Suspended users

Suspending an instructor does not automatically unpublish their existing courses.

Suspended users cannot perform authenticated LearnHub operations.

Publicly available course content remains accessible according to the course's
publication status, regardless of the instructor's current account status.
