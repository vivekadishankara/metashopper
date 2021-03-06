"""
This class contains the various tests for verifying different functionalities
"""
import os
import pytest
from pylint import epylint as lint
from framework.driver import Driver
import configuration
from sites.shops.amazon import Amazon
from sites.shops.flipkart import Flipkart
from sites.shops.snapdeal import Snapdeal
from api.models import Item, Result
from api import db

TEST_ITEMS = [
            'Honor 9n',
            'Honor 9',
            'Honor',
            'Washing machine',
            'shoes',
    ]

SHOPS = [
        Amazon,
        Flipkart,
        Snapdeal,
    ]


@pytest.fixture(scope='class')
def price_fixture():
    driver.start_driver()
    yield
    driver.quit()


class TestCode(object):
    """
    This class checks the code quality
    """
    def test_pylint_review(self):
        """
        This method lints the entire code. It requires that the pylint output does not have an error
        and the pylint score to be greater than 5.0
        :return: None
        """
        lint_stdout, lint_stderr = lint.py_run('..', return_std=True)
        for line in lint_stdout:
            if not line.isspace():
                spaced = line.split()
                assert 'error' not in spaced
        score = float(spaced[6].split('/')[0])
        assert score > 5.0
        print(line)


# @pytest.mark.usefixtures('price_fixture')
class TestPrice(object):
    """
    This class verifies the framework functionalities
    """
    @pytest.mark.parametrize('item', (['Redmi 5']))
    def test_search_basic(self, item):
        """
        This method tests the search functionality of the framework for all the shops for a given item
        :param item: item to be searched in the shops
        :return: writes the results into a file named 'results'
        """
        item_num = configuration.SEARCH_RESERVE
        fp = 'results'
        driver = Driver()
        with open(fp, 'w') as f, driver as d:
            for Shop in [Amazon, Flipkart, Snapdeal]:
                shop = Shop(d)
                shop.navigate()
                results = []
                for result in shop.search_results(item, item_num):
                    f.write(str(result) + '\n')
                    results.append(result)
                    for sub in shop.results_page.results.sub_elements:
                        assert result.get(sub) is not None
                assert len(results) == item_num

    @pytest.mark.parametrize('item', TEST_ITEMS)
    @pytest.mark.parametrize('shop', SHOPS)
    def test_search(self, item, shop):
        """
        This method tests the search functionality of the framework for a given shops and a given item
        :param item: item to be searched in the shop
        :param shop: shop to be searched
        :return: writes the results into a file named 'results1'
        """
        item_num = configuration.SEARCH_RESERVE
        fp = 'results1'
        driver = Driver()
        with open(fp, 'w') as f, driver as d:
            shopobj = shop(d)
            shopobj.navigate()
            results = []
            for result in shopobj.search_results(item, item_num):
                f.write(str(result) + '\n')
                results.append(result)
                for sub in shopobj.results_page.results.sub_elements:
                    assert result.get(sub) is not None
            assert len(results) == item_num


class TestApi(object):
    """
    This class tests the functionalities of the api
    """
    def test_db_basic(self):
        """
        This method verifies the database functionalities of the api
        :return: None
        """
        item = 'Redmi 5'
        fp = 'results'
        if not os.path.exists(fp):
            test_price_obj = TestPrice()
            test_price_obj.test_search_basic(item)

        results = []
        with open(fp) as f:
            for line in f:
                result = eval(line)
                if not result['stars']:
                    result['stars'] = 0.0
                results.append(result)

        it = Item.query.filter_by(itemname=item).first()
        if it:
            it.results.delete()
            db.session.commit()
        else:
            it = Item(itemname=item)
            db.session.add(it)
            db.session.commit()

        for i in range(len(results)):
            result_db = Result(shop='Snapdeal', search_item=it, **results[i])
            db.session.add(result_db)

        db.session.commit()

        it.results.delete()
        it.query.delete()
        db.session.commit()

    @pytest.mark.parametrize('item', TEST_ITEMS)
    @pytest.mark.parametrize('shop', SHOPS)
    def test_db(self, item, shop):
        """
        This method verifies the database functionalities of the api
        :return: None
        """
        fp = 'results1'
        test_price_obj = TestPrice()
        test_price_obj.test_search(item, shop)

        results = []
        with open(fp) as f:
            for line in f:
                result = eval(line)
                if not result['stars']:
                    result['stars'] = 0.0
                results.append(result)

        it = Item.query.filter_by(itemname=item).first()
        if it:
            it.results.delete()
            db.session.commit()
        else:
            it = Item(itemname=item)
            db.session.add(it)
            db.session.commit()

        for i in range(len(results)):
            result_db = Result(shop=shop.__name__, search_item=it, **results[i])
            db.session.add(result_db)

        db.session.commit()

        it.results.delete()
        it.query.delete()
        db.session.commit()
