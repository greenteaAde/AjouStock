# main_before.py
# 강화학습 전에 실행하는 모듈
# 주식 데이터를 읽고, 차트 데이터와 학습 데이터를 준비하고, 주식투자 강화학습을 실행하는 모듈
import os
import logging
from data import data_management
from learning import settings
from learner import Learner


if __name__ == '__main__':
    stock_code = '000810'  # 삼성화재

    # 로그 기록
    log_dir = os.path.join(settings.BASE_DIR, 'logs/%s' % stock_code)
    timestr = settings.get_time_str()
    if not os.path.exists('logs/%s' % stock_code):
        os.makedirs('logs/%s' % stock_code)
    file_handler = logging.FileHandler(filename=os.path.join(
        log_dir, "%s_%s.log" % (stock_code, timestr)), encoding='utf-8')
    stream_handler = logging.StreamHandler()
    file_handler.setLevel(logging.DEBUG)
    stream_handler.setLevel(logging.INFO)
    logging.basicConfig(format="%(message)s",
                        handlers=[file_handler, stream_handler], level=logging.DEBUG)

    # 데이터 준비
    chart_data = data_management.load_chart_data(
        os.path.join(settings.BASE_DIR, 'data/chart_data/{}.csv'.format(stock_code)))
    prep_data = data_management.preprocess(chart_data)
    training_data = data_management.build_training_data(prep_data)

    # 기간 필터링
    training_data = training_data[(training_data['date'] >= '2017-01-01') &
                                  (training_data['date'] <= '2017-12-31')]
    training_data = training_data.dropna()

    # 차트 데이터 분리
    features_chart_data = ['date', 'open', 'high', 'low', 'close', 'volume']
    chart_data = training_data[features_chart_data]

    # 학습 데이터 분리
    features_training_data = [
        'open_lastclose_ratio', 'high_close_ratio', 'low_close_ratio',
        'close_lastclose_ratio', 'volume_lastvolume_ratio',
        'close_ma5_ratio', 'volume_ma5_ratio',
        'close_ma10_ratio', 'volume_ma10_ratio',
        'close_ma20_ratio', 'volume_ma20_ratio',
        'close_ma60_ratio', 'volume_ma60_ratio',
        'close_ma120_ratio', 'volume_ma120_ratio']
    training_data = training_data[features_training_data]

    # 강화학습 시작
    policy_learner = Learner(
        stock_code=stock_code,              # 종목 코드
        chart_data=chart_data,              # 차트 데이터
        training_data=training_data,        # 학습 데이터
        min_trading_unit=1,                 # 최소 투자 단위
        max_trading_unit=2,                 # 최대 투자 단위
        delayed_reward_threshold=.2,        # 지연 보상 임계치
        lr=.001)                            # 학습 속도

    policy_learner.fit(balance=10000000,    # 초기 자본금
                       num_epoches=1000,    # 수행할 Epoch 수
                       discount_factor=0,   # 할인 요인
                       start_epsilon=.5)    # 초기 탐험률

    # 정책 신경망을 파일로 저장
    model_dir = os.path.join(settings.BASE_DIR, 'models/%s' % stock_code)
    if not os.path.isdir(model_dir):
        os.makedirs(model_dir)
    model_path = os.path.join(model_dir, 'model_%s.h5' % timestr)
    policy_learner.policy_network.save_model(model_path)