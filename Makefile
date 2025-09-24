.PHONY: bootstrap bot admin test package

bootstrap:
	bash scripts/bootstrap.sh

bot:
	bash scripts/run_bot.sh

admin:
	bash scripts/run_admin.sh

test:
	pytest

package:
	bash scripts/package.sh
